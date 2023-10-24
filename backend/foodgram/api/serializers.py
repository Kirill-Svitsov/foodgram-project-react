import webcolors
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import RegexValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingList, Tag
)
from users.models import CustomUser, Follow


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class CustomUserCreateSerializer(UserCreateSerializer):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message=(
            'Username должен содержать только буквы, цифры, '
            'и следующие символы: @ . + -'
        ),
    )

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'id', 'email', 'username',
            'password', 'first_name', 'last_name'
        )

    username = serializers.CharField(
        validators=[username_validator],
        max_length=150,
    )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.following.filter(author=obj).exists()
        return False

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            required=True
        ),
        write_only=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_id,
                amount=amount
            )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        if not ingredients_data:
            raise serializers.ValidationError("Ingredients are required.")
        if not tags_data:
            raise serializers.ValidationError("Tags are required.")
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient_id,
                amount=amount
            )
        instance.tags.set(tags_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Ingredients are required.")
        validated_ingredients = []
        existing_ingredient_ids = set()
        for ingredient_data in value:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            if not ingredient_id or not amount:
                raise serializers.ValidationError(
                    "All ingredient fields must be provided."
                )
            if ingredient_id in existing_ingredient_ids:
                raise serializers.ValidationError(
                    "Duplicate ingredient id detected."
                )
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError("Ingredient does not exist.")
            existing_ingredient_ids.add(ingredient_id)
            validated_ingredients.append({
                'id': ingredient.id,
                'amount': amount,
            })
        return validated_ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError("Tags are required.")
        tag_ids = set()
        for tag_id in tags:
            if tag_id in tag_ids:
                raise serializers.ValidationError("Duplicate tag id detected.")
            tag_ids.add(tag_id)
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                "Cooking time must be at least 1."
            )
        return cooking_time

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError("Image is required.")

        return image

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = CustomUserSerializer(
            instance.author,
            context=self.context
        ).data
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True,
            context=self.context
        ).data
        representation['ingredients'] = RecipeIngredientDetailSerializer(
            instance.recipeingredient_set.all(),
            many=True,
            context=self.context
        ).data
        return representation

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        return (user.is_anonymous
                and recipe.shopping_list.filter(user=user).exists())

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (user.is_anonymous
                and recipe.shopping_list.filter(user=user).exists())


class ShoppingListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class SubscribedAuthorsSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.following.filter(author=obj.author).exists()
        return False

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            "request"
        ).query_params.get("recipes_limit")
        if recipes_limit:
            recipes = obj.author.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.author.recipes.all()
        return RecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()
