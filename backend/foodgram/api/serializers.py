import webcolors
from django.db.transaction import atomic
from django.core.validators import RegexValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from constants import MIN_COOKING_TIME, MAX_COOKING_TIME
from recipes.models import (
    Ingredient, Recipe,
    RecipeIngredient, Tag, ShoppingList, Favorite
)
from users.models import User


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
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^[w.@+-]+Z',
                message=(
                    'Username должен содержать только буквы, цифры, '
                    'и следующие символы: @ . + -'
                ),
            )
        ]
    )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.following.filter(author=obj).exists()
        return False

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed'
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag"""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient"""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientDetailSerializer(serializers.ModelSerializer):
    """Сериализатор промежуточной модели RecipeIngredient"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
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
        read_only_fields = (
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
        user = self.context.get('request').user
        return not user.is_anonymous and (
            recipe.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return not user.is_anonymous and (
            recipe.shoppinglists.filter(user=user).exists()
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
        if not ingredients or len(ingredients) == 0:
            raise serializers.ValidationError(
                {
                    'ingredients':
                        'Список ингредиентов не может быть пустым.'
                }
            )
        # Проверка тегов
        tags = data.get('tags')
        if not tags or len(tags) == 0:
            raise serializers.ValidationError(
                {'tags': 'Список тегов не может быть пустым.'}
            )
        # Проверка на уникальность ингредиентов и тегов
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        tag_ids = [tag.id for tag in tags]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не могут повторяться.'}
            )
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {'tags': 'Теги не могут повторяться.'}
            )
        # Проверка поля image
        image = data.get('image')
        if not image:
            raise serializers.ValidationError(
                {'image': 'Поле image не может быть пустым.'}
            )
        # Проверка поля cooking_time
        cooking_time = data.get('cooking_time')
        if not cooking_time:
            raise serializers.ValidationError(
                {
                    'cooking_time':
                        'Поле cooking_time не может быть пустым.'
                }
            )
        return data

    @atomic
    def create(self, validate_data):
        tags = validate_data.pop('tags')
        ingredients = validate_data.pop('ingredients')
        recipe = Recipe.objects.create(**validate_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validate_data):
        tags = validate_data.pop('tags')
        ingredients = validate_data.pop('ingredients')
        recipe = super().update(recipe, validate_data)
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
        recipes_limit = self.context['request'].GET.get(
            'recipes_limit', default=3
        )
        recipes_user = user.recipes.all()[:int(recipes_limit)]
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


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для ShoppingList"""
    class Meta:
        model = ShoppingList
        fields = '__all__'

    def to_representation(self, recipe):
        return RecipeGetSerializer(
            recipe, context=self.context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для Favorite"""
    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, recipe):
        return RecipeGetSerializer(
            recipe, context=self.context
        ).data
