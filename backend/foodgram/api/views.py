from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from djoser.views import UserViewSet

from django.http import HttpResponse

from .permissions import (
    IsAuthorOrReadOnly,
    IsReadOnly, AllowAnyForCreate
)
from recipes.models import (
    ShoppingList, Ingredient, Recipe,
    RecipeIngredient, Tag, Favorite
)
from users.models import Follow, CustomUser
from .serializers import (
    CustomUserSerializer, TagSerializer,
    IngredientSerializer, RecipeIngredientSerializer, RecipeSerializer,
    ShoppingListSerializer, SubscribedAuthorsSerializer
)
from .pagination import CustomPageNumberPagination
from .generate_shopping_list import generate_csv


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAnyForCreate, ]
    pagination_class = CustomPageNumberPagination

    @action(detail=False, methods=['get'], url_path='me')
    def check_me(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'detail': 'Current_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(current_password, user.password):
            return Response(
                {'detail': 'Invalid current password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def get_subscriptions(self, request):
        subscriptions = Follow.objects.filter(user=request.user)
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(
            subscriptions,
            request
        )
        serializer = SubscribedAuthorsSerializer(
            result_page,
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
    )
    def manage_following(self, request, **kwargs):
        user = self.get_object()
        following = Follow.objects.filter(
            user=request.user, author=user
        ).exists()
        if request.method == "POST":
            if user == request.user:
                return Response(
                    {"detail": "You can not subscribe for yourself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not following:
                obj = Follow.objects.create(
                    user=request.user, author=user)
                serializer = SubscribedAuthorsSerializer(
                    obj, context={"request": request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "You already subscribe for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if not following:
            return Response(
                {"detail": "You dont subscribe for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.filter(user=request.user, author=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = CustomPageNumberPagination
    ordering = ['-pub_date']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, **kwargs):
        recipe = self.get_object()
        in_shopping_list = ShoppingList.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()
        if request.method == "POST":
            if not in_shopping_list:
                obj = ShoppingList.objects.create(
                    user=request.user, recipe=recipe)
                serializer = ShoppingListSerializer(
                    obj, context={"request": request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "This recipe already in your shopping list."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if not in_shopping_list:
            return Response(
                {"detail": "This recipe not in your shopping list."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingList.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request, **kwargs):
        shopping_list = ShoppingList.objects.filter(user=request.user)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.csv"'
        )
        generate_csv(shopping_list, response)
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def add_or_remove_from_favorites(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if created:
                return Response(
                    {"detail": "Recipe added to favorites successfully."},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"detail": "Recipe is already in favorites."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(
                    user=request.user,
                    recipe=recipe
                )
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {"detail": "Recipe is not in favorites."},
                    status=status.HTTP_400_BAD_REQUEST
                )


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
