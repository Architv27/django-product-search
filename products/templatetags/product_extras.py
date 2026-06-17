from django import template

from products.constants import TagIcons

register = template.Library()


@register.filter
def tag_icon(tag):
    """Return the Material Symbol name for a tag (by slug), or a default."""
    slug = getattr(tag, "slug", "") or ""
    return TagIcons.BY_SLUG.get(slug, TagIcons.DEFAULT)
