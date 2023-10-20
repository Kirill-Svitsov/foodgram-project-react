from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe
from users.models import CustomUser


# from django_filters.rest_framework import FilterSet, filters
#
# from recipes.models import Ingredient, Recipe, Tag
#
#
# class IngredientFilter(FilterSet):
#     name = filters.CharFilter(lookup_expr='istartswith')
#
#     class Meta:
#         model = Ingredient
#         fields = ('name',)
#
#
# class RecipeFilter(FilterSet):
#     tags = filters.ModelMultipleChoiceFilter(
#         field_name='tags__slug',
#         to_field_name='slug',
#         queryset=Tag.objects.all()
#     )
#     is_favorited = filters.BooleanFilter(
#         field_name='is_favorited',
#         method='filter_is_favorited'
#     )
#     is_in_shopping_cart = filters.BooleanFilter(
#         method='filter_is_in_shopping_cart'
#     )
#
#     class Meta:
#         model = Recipe
#         fields = ['tags', 'is_favorited', 'is_in_shopping_cart']
#
#     def filter_is_favorited(self, queryset, name, value):
#         user = self.request.user
#         if user.is_authenticated and value:
#             return queryset.filter(is_favorited__user=user)
#         else:
#             return queryset
#
#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         user = self.request.user
#         if user.is_authenticated and value:
#             return queryset.filter(is_in_shopping_cart__user=user)
#         else:
#             return queryset


class IngredientFilter(filters.FilterSet):
    """Фильтр для модели ингредиентов."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для модели рецептов."""

    author = filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация избранных рецептов."""
        if value:
            return queryset.filter(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов в корзине покупок."""
        if value:
            return queryset.filter(shoppingcart__user=self.request.user)
