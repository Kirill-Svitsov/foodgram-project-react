from django.http import HttpResponse
from django.shortcuts import get_object_or_404
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
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite, Ingredient,
    Recipe, ShoppingList,
    Tag
)
from users.models import Follow, User


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели User"""
    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def current_user(self, request):
        """
        Метод необходим для обработки исключения на api/users/me/.
        В случае если юзер будет неавторизован, вернется
        иключение 401, а без этого метода 500.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        author = get_object_or_404(User, pk=id)
        # Проверка на попытку подписаться на себя
        if request.user == author:
            return Response(
                {
                    'detail':
                        'Вы не можете подписаться на самого себя.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Проверка на уже существующую подписку
        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=request.user,
            author=author
        )

        serializer = serializers.UserRecipesSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Метод для отписки от Автора"""
        author = get_object_or_404(User, pk=id)
        # Проверка, что подписка существует
        if not Follow.objects.filter(
                user=request.user,
                author=author
        ).exists():
            return Response(
                {
                    'detail':
                        'Вы уже подписаны на этого пользователя.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
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
    pagination_class = CustomPageNumberPagination
    filter_backends = (django_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Получение сериализатора в зависимости от запроса"""
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeGetSerializer
        return serializers.RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['POST'],
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk):
        """Метод добавления рецепта в список покупок"""
        recipe = get_object_or_404(Recipe, id=pk)
        if ShoppingList.objects.filter(
                user=request.user,
                recipe=recipe
        ).exists():
            return Response(
                {''
                 'detail':
                     'Рецепт с указанным ID уже в списке покупок.'
                 },
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingList.objects.create(
            user=request.user,
            recipe=recipe
        )
        serializer = serializers.RecipeGetSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Метод удаления рецепта из списка покупок"""
        get_object_or_404(ShoppingList,
                          recipe=pk,
                          user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request, **kwargs):
        """Метод для скачивания списка покупок"""
        shopping_list = ShoppingList.objects.filter(
            user=request.user
        )
        shopping_list_text = generate_shopping_list(
            shopping_list
        )
        response = HttpResponse(
            shopping_list_text,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt'
        )
        return response

    @action(
        detail=True,
        methods=['POST'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Метод добавления рецепта в избранное"""
        recipe = get_object_or_404(Recipe, id=pk)
        # Проверка, добавлен ли рецепт в избранное
        if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
        ).exists():
            return Response(
                {
                    'detail':
                        'Этот рецепт уже добавлен в избранное.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(
            user=request.user,
            recipe=recipe
        )
        serializer = serializers.RecipeGetSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Метод удаления рецепта из избранного"""
        get_object_or_404(Favorite,
                          recipe=pk,
                          user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
