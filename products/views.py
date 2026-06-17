from django.core.paginator import Paginator
from django.shortcuts import render

from . import search
from .constants import (
    ProductContextKeys,
    ProductFilterQueryParams,
    ProductSearch,
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

    search_tokens = search.tokenize(description_search_term)

    matched_products = (
        Product.objects
        .select_related("category")
        .prefetch_related("tags")
        .apply_product_filters(
            search_tokens=search_tokens,
            selected_category_slug=selected_category_slug,
            selected_tag_slugs=selected_tag_slugs,
        )
    )

    # Rank in Python only when searching (SQLite can't order by relevance);
    # otherwise keep the model's default ordering.
    if search_tokens:
        ranked_products = search.rank(matched_products, search_tokens)
    else:
        ranked_products = matched_products

    paginator = Paginator(ranked_products, ProductSearch.PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get(ProductFilterQueryParams.PAGE))

    # "Did you mean" only when a non-empty search returned no results.
    suggestion = None
    if search_tokens and paginator.count == 0:
        suggestion = search.suggest(search_tokens, search.build_vocabulary())

    context = {
        ProductContextKeys.PRODUCTS: page_obj,
        ProductContextKeys.PAGE_OBJ: page_obj,
        ProductContextKeys.CATEGORIES: Category.objects.all(),
        ProductContextKeys.TAGS: Tag.objects.all(),
        ProductContextKeys.DESCRIPTION_SEARCH_TERM: description_search_term,
        ProductContextKeys.SELECTED_CATEGORY_SLUG: selected_category_slug,
        ProductContextKeys.SELECTED_TAG_SLUGS: selected_tag_slugs,
        ProductContextKeys.SUGGESTION: suggestion,
        ProductContextKeys.QUERYSTRING: _filters_querystring(request),
    }

    return render(
        request,
        ProductTemplatePaths.PRODUCT_LIST,
        context,
    )


def _filters_querystring(request):
    """Current query params minus ``page``, for pagination links that keep filters."""
    params = request.GET.copy()
    params.pop(ProductFilterQueryParams.PAGE, None)
    return params.urlencode()
