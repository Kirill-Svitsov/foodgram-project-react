from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (
    Tag, Ingredient, Recipe,
    RecipeIngredient, Favorite, ShoppingList
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    list_display_links = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "name",
        "image_tag",
        "text",
        "cooking_time",
        "pub_date",
        "favorites_count",
    )
    search_fields = ("name",)
    list_filter = ("author", "name", "tags")
    list_display_links = ("name",)
    inlines = (RecipeIngredientInline,)

    def favorites_count(self, obj):
        return obj.favorite.count()

    favorites_count.short_description = "Добавлено в избранное"

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="80" height="60">')

    image_tag.short_description = 'Изображение'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name", "measurement_unit")
    list_display_links = ("name",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "user",
    )
    search_fields = ("recipe",)
    list_filter = ("recipe", "user")


@admin.register(ShoppingList)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "user",
    )
    search_fields = ("recipe",)
    list_filter = ("recipe", "user")
