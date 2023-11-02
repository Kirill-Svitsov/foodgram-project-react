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
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'image_tag',
        'text',
        'cooking_time',
        'pub_date',
        'favorites_count',
        'ingredients_list',
        'tags_list',
    )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    list_display_links = ('name',)
    inlines = (RecipeIngredientInline,)

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, obj):
        return obj.favorite.count()

    @admin.display(description='Изображение')
    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="80" height="60">')

    @admin.display(description='Ингредиенты')
    def ingredients_list(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name', 'measurement_unit')
    list_display_links = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = ('recipe',)
    list_filter = ('recipe', 'user')


@admin.register(ShoppingList)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = ('recipe',)
    list_filter = ('recipe', 'user')
