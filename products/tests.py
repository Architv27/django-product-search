from django.test import TestCase
from django.urls import reverse

from . import search
from .constants import ProductSearch
from .models import Category, Product, Tag


class TokenizeTests(TestCase):
    def test_lowercases_and_splits_on_non_word(self):
        self.assertEqual(search.tokenize("Copper, Conduit!"), ["copper", "conduit"])

    def test_drops_short_tokens_and_dedupes(self):
        self.assertEqual(search.tokenize("a copper copper"), ["copper"])

    def test_caps_token_count(self):
        many = " ".join("word%d" % i for i in range(ProductSearch.MAX_TOKENS + 5))
        self.assertEqual(len(search.tokenize(many)), ProductSearch.MAX_TOKENS)

    def test_empty_and_all_short(self):
        self.assertEqual(search.tokenize(""), [])
        self.assertEqual(search.tokenize("a !"), [])


class SearchFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.wire_cat = Category.objects.create(name="Wire & Cable", slug="wire-cable")
        cls.conduit_cat = Category.objects.create(name="Conduit", slug="conduit")
        cls.copper_tag = Tag.objects.create(name="Copper", slug="copper")
        cls.outdoor_tag = Tag.objects.create(name="Outdoor", slug="outdoor")

        cls.copper_wire = Product.objects.create(
            name="Copper Wire",
            description="Stranded building wire.",
            category=cls.wire_cat,
        )
        cls.copper_wire.tags.add(cls.copper_tag)

        cls.emt = Product.objects.create(
            name="EMT Conduit",
            description="Steel tubing with a copper ground.",
            category=cls.conduit_cat,
        )
        cls.emt.tags.add(cls.outdoor_tag, cls.copper_tag)  # two tags, for ALL/ANY tests

        cls.pvc = Product.objects.create(
            name="PVC Conduit",
            description="Plastic outdoor conduit.",
            category=cls.conduit_cat,
        )
        cls.pvc.tags.add(cls.outdoor_tag)

    def _ids(self, queryset):
        return {product.id for product in queryset}

    def test_search_matches_name_and_description(self):
        tokens = search.tokenize("copper")
        results = Product.objects.apply_product_filters(search_tokens=tokens)
        # "Copper Wire" (name) + "EMT Conduit" (description: "copper ground")
        self.assertEqual(self._ids(results), {self.copper_wire.id, self.emt.id})

    def test_multi_token_requires_all(self):
        tokens = search.tokenize("copper wire")
        results = Product.objects.apply_product_filters(search_tokens=tokens)
        self.assertEqual(self._ids(results), {self.copper_wire.id})

    def test_filter_by_category(self):
        results = Product.objects.apply_product_filters(selected_category_slug="conduit")
        self.assertEqual(self._ids(results), {self.emt.id, self.pvc.id})

    def test_filter_by_any_tag(self):
        results = Product.objects.apply_product_filters(selected_tag_slugs=["outdoor"])
        self.assertEqual(self._ids(results), {self.emt.id, self.pvc.id})

    def test_match_any_is_union_of_tags(self):
        results = Product.objects.apply_product_filters(
            selected_tag_slugs=["outdoor", "copper"], match_all_tags=False
        )
        self.assertEqual(
            self._ids(results), {self.emt.id, self.pvc.id, self.copper_wire.id}
        )

    def test_match_all_requires_every_tag(self):
        results = Product.objects.apply_product_filters(
            selected_tag_slugs=["outdoor", "copper"], match_all_tags=True
        )
        self.assertEqual(self._ids(results), {self.emt.id})

    def test_combined_search_category_tag(self):
        tokens = search.tokenize("conduit")
        results = Product.objects.apply_product_filters(
            search_tokens=tokens,
            selected_category_slug="conduit",
            selected_tag_slugs=["outdoor"],
        )
        self.assertEqual(self._ids(results), {self.emt.id, self.pvc.id})


class RankingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Cat", slug="cat")
        cls.name_hit = Product.objects.create(
            name="Copper Lug", description="A connector.", category=category,
        )
        cls.description_hit = Product.objects.create(
            name="Steel Clamp", description="Holds copper cable.", category=category,
        )

    def test_name_match_ranks_above_description_match(self):
        tokens = search.tokenize("copper")
        ranked = search.rank([self.description_hit, self.name_hit], tokens)
        self.assertEqual(ranked[0], self.name_hit)


class SuggestionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Conduit", slug="conduit")
        Product.objects.create(name="EMT Conduit", description="Steel tubing.", category=category)

    def test_suggests_correction_for_typo(self):
        vocabulary = search.build_vocabulary()
        self.assertEqual(search.suggest(["condiut"], vocabulary), "conduit")

    def test_no_suggestion_for_known_term(self):
        vocabulary = search.build_vocabulary()
        self.assertIsNone(search.suggest(["conduit"], vocabulary))


class ProductListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Cat", slug="cat")
        for index in range(ProductSearch.DEFAULT_PAGE_SIZE + 3):
            Product.objects.create(
                name="Item %02d" % index, description="desc", category=category,
            )

    def test_first_page_is_full(self):
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.status_code, 200)
        page_obj = response.context["page_obj"]
        self.assertEqual(len(page_obj), ProductSearch.DEFAULT_PAGE_SIZE)
        self.assertEqual(page_obj.paginator.count, ProductSearch.DEFAULT_PAGE_SIZE + 3)

    def test_second_page_has_remainder(self):
        response = self.client.get(reverse("products:product_list"), {"page": 2})
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_per_page_overrides_page_size(self):
        response = self.client.get(reverse("products:product_list"), {"per_page": 4})
        self.assertEqual(len(response.context["page_obj"]), 4)

    def test_per_page_is_clamped_to_max(self):
        response = self.client.get(reverse("products:product_list"), {"per_page": 10000})
        self.assertLessEqual(
            len(response.context["page_obj"]), ProductSearch.MAX_PAGE_SIZE
        )

    def test_did_you_mean_shown_on_empty_results(self):
        conduit_cat = Category.objects.create(name="Conduit", slug="conduit")
        Product.objects.create(name="EMT Conduit", description="x", category=conduit_cat)
        response = self.client.get(reverse("products:product_list"), {"q": "condiut"})
        self.assertEqual(response.context["page_obj"].paginator.count, 0)
        self.assertEqual(response.context["suggestion"], "conduit")
