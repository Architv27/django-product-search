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