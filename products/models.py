from django.db import models
from django.db.models import Q

from .constants import ProductFieldLimits


class ProductQuerySet(models.QuerySet):
    def search(self, search_tokens):
        """Text search across product name and description.

        Tokenized: every token must match (AND across tokens), each token
        matching the name OR the description (OR across fields). This satisfies
        "search products by description" and additionally covers the name.
        An empty/None token list is a no-op (returns the queryset unchanged).

        (Conjunctive boolean retrieval -- what an inverted index / FTS does;
        here SQLite LIKE narrows the candidate set the view then ranks.)
        """
        if not search_tokens:
            return self

        predicate = Q()
        for token in search_tokens:
            predicate &= Q(name__icontains=token) | Q(description__icontains=token)
        return self.filter(predicate)

    def filter_by_category_slug(self, selected_category_slug):
        """Restrict to a single category by slug. Blank slug is a no-op."""
        selected_category_slug = (selected_category_slug or "").strip()
        if not selected_category_slug:
            return self

        return self.filter(category__slug=selected_category_slug)

    def filter_by_any_tag_slug(self, selected_tag_slugs):
        """Restrict to products having ANY of the selected tags (OR semantics).

        Blank entries are dropped; an empty list is a no-op. ``.distinct()``
        collapses the duplicate rows the many-to-many join can produce.
        """
        cleaned_slugs = [slug.strip() for slug in (selected_tag_slugs or []) if slug and slug.strip()]
        if not cleaned_slugs:
            return self

        return self.filter(tags__slug__in=cleaned_slugs).distinct()

    def apply_product_filters(
        self,
        search_tokens=None,
        selected_category_slug="",
        selected_tag_slugs=None,
    ):
        """Compose the three independent filters: search AND category AND tags.

        Each filter is a no-op when its input is empty, so any combination
        (including none) works -- the requirement's "combine search and filter".
        """
        return (
            self.search(search_tokens)
            .filter_by_category_slug(selected_category_slug)
            .filter_by_any_tag_slug(selected_tag_slugs)
        )


class Category(models.Model):
    name = models.CharField(
        max_length=ProductFieldLimits.CATEGORY_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        max_length=ProductFieldLimits.CATEGORY_SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=ProductFieldLimits.TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        max_length=ProductFieldLimits.TAG_SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        max_length=ProductFieldLimits.PRODUCT_NAME_MAX_LENGTH,
        db_index=True,
    )
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="products",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name