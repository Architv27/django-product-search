from django.core.paginator import Paginator
from django.shortcuts import render

from . import search
from .constants import (
    ProductContextKeys,
    ProductFilterQueryParams,
    ProductSearch,
    ProductTagMatch,
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

    tag_match = request.GET.get(
        ProductFilterQueryParams.MATCH,
        ProductTagMatch.DEFAULT,
    )
    if tag_match not in (ProductTagMatch.ANY, ProductTagMatch.ALL):
        tag_match = ProductTagMatch.DEFAULT
    match_all_tags = tag_match == ProductTagMatch.ALL

    search_tokens = search.tokenize(description_search_term)

    matched_products = (
        Product.objects
        .select_related("category")
        .prefetch_related("tags")
        .apply_product_filters(
            search_tokens=search_tokens,
            selected_category_slug=selected_category_slug,
            selected_tag_slugs=selected_tag_slugs,
            match_all_tags=match_all_tags,
        )
    )

    # Rank in Python only when searching (SQLite can't order by relevance);
    # otherwise keep the model's default ordering.
    if search_tokens:
        ranked_products = search.rank(matched_products, search_tokens)
    else:
        ranked_products = matched_products

    page_size = _resolve_page_size(request)
    paginator = Paginator(ranked_products, page_size)
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
        ProductContextKeys.PER_PAGE: page_size,
        ProductContextKeys.MAX_PAGE_SIZE: ProductSearch.MAX_PAGE_SIZE,
        ProductContextKeys.TAG_MATCH: tag_match,
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


def _resolve_page_size(request):
    """Page size from ?per_page (set client-side to keep a full NxN grid),
    clamped to a safe range; falls back to the default when absent/invalid."""
    try:
        size = int(request.GET.get(ProductFilterQueryParams.PER_PAGE))
    except (TypeError, ValueError):
        return ProductSearch.DEFAULT_PAGE_SIZE
    return max(ProductSearch.MIN_PAGE_SIZE, min(size, ProductSearch.MAX_PAGE_SIZE))
