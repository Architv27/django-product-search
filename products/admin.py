from django.contrib import admin

from .constants import ProductModelFields
from .models import Category, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        ProductModelFields.NAME,
        ProductModelFields.SLUG,
    ]
    search_fields = [
        ProductModelFields.NAME,
    ]
    prepopulated_fields = {
        ProductModelFields.SLUG: [
            ProductModelFields.NAME,
        ],
    }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        ProductModelFields.NAME,
        ProductModelFields.SLUG,
    ]
    search_fields = [
        ProductModelFields.NAME,
    ]
    prepopulated_fields = {
        ProductModelFields.SLUG: [
            ProductModelFields.NAME,
        ],
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        ProductModelFields.NAME,
        ProductModelFields.CATEGORY,
        ProductModelFields.CREATED_AT,
        ProductModelFields.UPDATED_AT,
    ]
    list_filter = [
        ProductModelFields.CATEGORY,
        ProductModelFields.TAGS,
    ]
    search_fields = [
        ProductModelFields.NAME,
        ProductModelFields.DESCRIPTION,
    ]
    filter_horizontal = [
        ProductModelFields.TAGS,
    ]