from rest_framework import serializers

from recipes.models import Ingredient


# При импорте этих функций и добавлении их в поля сериализаторв
# возникают ошибки, поэтому код я оставил, но импортировать не стал,
# а разместил валидацию внутри сериализатора

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
            raise serializers.ValidationError(
                "Ingredient does not exist."
            )

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
            raise serializers.ValidationError(
                "Duplicate tag id detected."
            )
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
        raise serializers.ValidationError(
            "Image is required."
        )

    return image
