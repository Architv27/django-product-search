class ProductFieldLimits:
    CATEGORY_NAME_MAX_LENGTH = 100
    CATEGORY_SLUG_MAX_LENGTH = 120
    TAG_NAME_MAX_LENGTH = 100
    TAG_SLUG_MAX_LENGTH = 120
    PRODUCT_NAME_MAX_LENGTH = 150


class ProductFilterQueryParams:
    DESCRIPTION_SEARCH = "q"
    CATEGORY = "category"
    TAGS = "tags"
    PAGE = "page"


class ProductSearch:
    # Tokenization
    MIN_TOKEN_LEN = 2
    MAX_TOKENS = 12

    # Relevance weights (name matches outrank description matches)
    NAME_WEIGHT = 10
    DESCRIPTION_WEIGHT = 3
    ALL_TOKENS_IN_NAME_BONUS = 5
    EXACT_NAME_BONUS = 25

    # Pagination
    PAGE_SIZE = 8

    # Fuzzy "did you mean" similarity threshold (0..1)
    FUZZY_CUTOFF = 0.72


class TagIcons:
    """Material Symbol per tag (by slug) so chips are visually distinguishable."""

    DEFAULT = "sell"
    BY_SLUG = {
        "copper": "cable",
        "aluminum": "layers",
        "indoor": "home",
        "outdoor": "park",
        "weatherproof": "umbrella",
        "ul-listed": "verified",
        "residential": "cottage",
        "commercial": "apartment",
        "low-voltage": "electric_bolt",
        "in-stock": "inventory_2",
    }


class ProductTemplatePaths:
    PRODUCT_LIST = "products/product_list.html"


class ProductModelFields:
    NAME = "name"
    SLUG = "slug"
    DESCRIPTION = "description"
    CATEGORY = "category"
    TAGS = "tags"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class ProductContextKeys:
    PRODUCTS = "products"
    CATEGORIES = "categories"
    TAGS = "tags"
    DESCRIPTION_SEARCH_TERM = "description_search_term"
    SELECTED_CATEGORY_SLUG = "selected_category_slug"
    SELECTED_TAG_SLUGS = "selected_tag_slugs"
    PAGE_OBJ = "page_obj"
    SUGGESTION = "suggestion"
    QUERYSTRING = "querystring"
