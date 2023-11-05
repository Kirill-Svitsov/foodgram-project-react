from django.db.models import Sum
from django.http import FileResponse
from django_filters import rest_framework as django_filters
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api import serializers
from api.filters import IngredientFilter, RecipeFilter
from api.generate_shopping_list import generate_shopping_list
from api.pagination import PageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite, Ingredient,
    Recipe, ShoppingList,
    Tag, RecipeIngredient
)
from users.models import Follow, User


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели User"""
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Метод для получения списка подписок"""
        authors = User.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(authors)
        serializer = serializers.UserRecipesSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Метод для создания подписки"""
        data = {'user': request.user.id, 'author': id}
        serializer = serializers.FollowSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Метод для отписки от Автора"""
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=id
        )
        if not subscription.exists():
            return Response(
                {
                    'detail':
                        'Вы не подписаны на этого пользователя.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        subscription.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Tag"""
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (
        django_filters.DjangoFilterBackend,
        SearchFilter
    )
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipe"""
    permission_classes = (
        IsAuthorOrReadOnly,
        IsAuthenticatedOrReadOnly
    )
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'tags',
        'recipe_ingredients',
        'recipe_ingredients__ingredient'
    ).all()
    pagination_class = PageNumberPagination
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Получение сериализатора в зависимости от запроса"""
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeGetSerializer
        return serializers.RecipeCreateSerializer

    @staticmethod
    def create_item(serializer_class, request, pk):
        user = request.user
        data = {'user': user.id, 'recipe': pk}
        serializer = serializer_class(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Метод добавления рецепта в список покупок"""
        return self.create_item(
            serializers.ShoppingListSerializer, request, pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Метод удаления рецепта из списка покупок"""
        shopping_list = ShoppingList.objects.filter(
            recipe=pk,
            user=request.user
        )
        if shopping_list.exists():
            shopping_list.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request, **kwargs):
        ingredients_qs = RecipeIngredient.objects.filter(
            recipe__in=request.user.shoppinglists.values('recipe')
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list_text = generate_shopping_list(
            ingredients_qs,
            request.user.shoppinglists.all()
        )

        response = FileResponse(
            shopping_list_text,
            as_attachment=True,
            filename='shopping_cart.txt',
            content_type='text/plain'
        )

        return response

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Метод добавления рецепта в избранное"""
        return self.create_item(
            serializers.FavoriteSerializer, request, pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Метод удаления рецепта из избранного"""
        favorite = Favorite.objects.filter(
            recipe=pk,
            user=request.user
        )
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
