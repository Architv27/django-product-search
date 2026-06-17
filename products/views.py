from django.shortcuts import render

from .constants import (
    ProductContextKeys,
    ProductFilterQueryParams,
    ProductTemplatePaths,
)
from .models import Category, Product, Tag


def product_list(request):
    description_search_term = request.GET.get(
        ProductFilterQueryParams.DESCRIPTION_SEARCH,
        "",
    ).strip()

    selected_category_slug = request.GET.get(
        ProductFilterQueryParams.CATEGORY,
        "",
    ).strip()

    selected_tag_slugs = request.GET.getlist(
        ProductFilterQueryParams.TAGS,
    )

    products = (
        Product.objects
        .select_related("category")
        .prefetch_related("tags")
        .apply_product_filters(
            description_search_term=description_search_term,
            selected_category_slug=selected_category_slug,
            selected_tag_slugs=selected_tag_slugs,
        )
    )

    context = {
        ProductContextKeys.PRODUCTS: products,
        ProductContextKeys.CATEGORIES: Category.objects.all(),
        ProductContextKeys.TAGS: Tag.objects.all(),
        ProductContextKeys.DESCRIPTION_SEARCH_TERM: description_search_term,
        ProductContextKeys.SELECTED_CATEGORY_SLUG: selected_category_slug,
        ProductContextKeys.SELECTED_TAG_SLUGS: selected_tag_slugs,
    }

    return render(
        request,
        ProductTemplatePaths.PRODUCT_LIST,
        context,
    )