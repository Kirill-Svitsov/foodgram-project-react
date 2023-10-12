from django.http import request

import csv


def generate_csv(shopping_list, response):
    headers = [
        'Название',
        'Изображение',
        'Время приготовления (в минутах)',
        'Ингредиенты',
        'Описание'
    ]
    writer = csv.writer(response)
    writer.writerow(headers)
    ingredients_dict = {}
    for item in shopping_list:
        recipe = item.recipe
        name = recipe.name
        image_url = request.build_absolute_uri(
            recipe.get_image_url()
        ) if recipe.image else ''
        cooking_time = recipe.cooking_time
        description = recipe.text
        for ri in recipe.recipeingredient_set.all():
            ingredient_name = ri.ingredient.name
            ingredient_unit = ri.ingredient.measurement_unit
            amount = ri.amount
            if (ingredient_name, ingredient_unit) in ingredients_dict:
                ingredients_dict[(ingredient_name, ingredient_unit)] += amount
            else:
                ingredients_dict[(ingredient_name, ingredient_unit)] = amount
        writer.writerow([name, image_url, cooking_time, description])
    for (ingredient_name, ingredient_unit), amount in ingredients_dict.items():
        writer.writerow(
            ['* ' f"{ingredient_name} ({amount} {ingredient_unit})", '']
        )
