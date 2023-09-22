from rest_framework import serializers
from djoser.serializers import UserSerializer

from .models import *


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ['author', 'title', 'image', 'description', 'cooking_time', 'ingredients', 'tags']
        read_only_fields = ('author',)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_data['ingredient']['name'],
                unit=ingredient_data['ingredient']['unit']
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )
        recipe.tags.set(tags_data)

        return recipe
