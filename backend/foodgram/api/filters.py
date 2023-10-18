from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_tags(self, queryset, name, value):
        if value:
            tags = value.split(',')
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset
