import csv

from recipes.models import Ingredient


def generate_csv(shopping_list, response):
    writer = csv.writer(response)
    writer.writerow(['Ингредиент', 'Количество'])

    ingredient_dict = {}

    for item in shopping_list:
        ingredients = item['recipe']['ingredients']
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']

            if ingredient_id in ingredient_dict:
                ingredient_dict[ingredient_id] += amount
            else:
                ingredient_dict[ingredient_id] = amount

    for ingredient_id, amount in ingredient_dict.items():
        ingredient = Ingredient.objects.get(id=ingredient_id)
        writer.writerow([f'{ingredient.name} ({ingredient.measurement_unit})', amount])
