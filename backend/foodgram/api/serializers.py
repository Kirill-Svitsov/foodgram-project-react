import webcolors
from django.db.transaction import atomic
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from constants import (
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MAX_AMOUNT
)
from recipes.models import (
    Ingredient, Recipe,
    RecipeIngredient, Tag, ShoppingList, Favorite
)
from users.models import User, Follow


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError(
                'Для этого цвета нет имени'
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
                request and request.user.is_authenticated
                and request.user.following.filter(author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag"""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели RecipeIngredient"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов в рецепт """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для GET запросов"""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()
    image = Base64ImageField()
    ingredients = RecipeIngredientDetailSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (
                request and request.user.is_authenticated
                and recipe.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        return (
                request and request.user.is_authenticated
                and recipe.shoppinglists.filter(user=request.user).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/изменения рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        # Проверка ингредиентов
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients':
                        'Список ингредиентов не может быть пустым.'
                }
            )
        # Проверка тегов
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Список тегов не может быть пустым.'}
            )
        # Проверка на уникальность ингредиентов и тегов
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не могут повторяться.'}
            )
        if len(set(tag.id for tag in tags)) != len(tags):
            raise serializers.ValidationError(
                {'tags': 'Теги не могут повторяться.'}
            )
        return data

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                {'image': 'Поле image не может быть пустым.'}
            )
        return image

    @atomic
    def create(self, validate_data):
        tags = validate_data.pop('tags')
        ingredients = validate_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validate_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @atomic
    def update(self, recipe, validate_data):
        tags = validate_data.pop('tags')
        ingredients = validate_data.pop('ingredients')
        super().update(recipe, validate_data)
        recipe.tags.set(tags)
        recipe.recipe_ingredients.all().delete()
        self.create_ingredients(ingredients, recipe)
        return recipe

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def to_representation(self, recipe):
        return RecipeGetSerializer(
            recipe, context=self.context
        ).data


class UserRecipesSerializer(UserSerializer):
    """Сериализтор пользователя с рецептом и счетчиком"""
    recipes = serializers.SerializerMethodField(
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, user):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
            if recipes_limit < 0:
                recipes_limit = None
        except (TypeError, ValueError):
            recipes_limit = None
        recipes_user = (user.recipes.all()[:recipes_limit]
                        if recipes_limit else user.recipes.all())

        return ShortRecipeSerializer(
            recipes_user,
            many=True
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор сжатой версии рецепта"""
    image = Base64ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        if not User.objects.filter(pk=author.id).exists():
            raise serializers.ValidationError(
                'Автор не существует.',
                code=status.HTTP_404_NOT_FOUND
            )
        elif Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def to_representation(self, instance):
        return UserRecipesSerializer(
            instance.author,
            context=self.context
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('recipe', 'user')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingList.objects.filter(
                user=user.pk,
                recipe=recipe.pk
        ).exists():
            raise serializers.ValidationError(
                {'detail': 'Рецепт уже добавлен в список покупок.'},
                code=status.HTTP_400_BAD_REQUEST,
            )
        elif not Recipe.objects.filter(pk=recipe.pk).exists():
            raise serializers.ValidationError(
                {'detail': 'Рецепт не существует.'},
                code=status.HTTP_404_NOT_FOUND,
            )
        return data

    @staticmethod
    def create_item(user, recipe):
        ShoppingList.objects.create(user=user, recipe=recipe)


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(user=user.pk, recipe=recipe.pk).exists():
            raise serializers.ValidationError(
                {'detail': 'Рецепт уже добавлен в избранное.'}
            )
        elif not Recipe.objects.filter(pk=recipe.pk).exists():
            raise serializers.ValidationError(
                {'detail': 'Рецепт не существует.'},
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    @staticmethod
    def create_item(user, recipe):
        Favorite.objects.create(user=user, recipe=recipe)
