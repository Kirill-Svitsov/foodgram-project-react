import json

from recipes.models import Ingredient


def load_data_from_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
        for item in data:
            ingredient = Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            ingredient.save()


load_data_from_json('ingredients.json')
