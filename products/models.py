from django.db import models

from .constants import ProductFieldLimits


class ProductQuerySet(models.QuerySet):
    def search_by_description(self, description_search_term):
        if not description_search_term:
            return self

        return self.filter(description__icontains=description_search_term)

    def filter_by_category_slug(self, selected_category_slug):
        if not selected_category_slug:
            return self

        return self.filter(category__slug=selected_category_slug)

    def filter_by_any_tag_slug(self, selected_tag_slugs):
        if not selected_tag_slugs:
            return self

        return self.filter(tags__slug__in=selected_tag_slugs).distinct()

    def apply_product_filters(
        self,
        description_search_term="",
        selected_category_slug="",
        selected_tag_slugs=None,
    ):
        selected_tag_slugs = selected_tag_slugs or []

        return (
            self.search_by_description(description_search_term)
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