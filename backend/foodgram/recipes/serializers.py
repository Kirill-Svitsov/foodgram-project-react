from rest_framework import serializers
from djoser.serializers import UserSerializer
from djoser.serializers import UserCreateSerializer
from django.core.validators import RegexValidator

from .models import *


class CustomUserCreateSerializer(UserCreateSerializer):
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message=(
            'Username должен содержать только буквы, цифры, '
            'и следующие символы: @ . + -'
        ),
    )

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'password', 'first_name', 'last_name')

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
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        recipe.tags.set(tags_data)

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = CustomUserSerializer(instance.author, context=self.context).data
        representation['tags'] = TagSerializer(instance.tags.all(),
                                               many=True, context=self.context).data
        representation['ingredients'] = RecipeIngredientSerializer(instance.recipeingredient_set.all(), many=True,
                                                                   context=self.context).data
        return representation


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = '__all__'
