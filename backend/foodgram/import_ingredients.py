import csv

from recipes.models import Ingredient

with open('data/ingredients.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        name, measurement_unit = row
        ingredient, created = Ingredient.objects.get_or_create(
            name=name,
            measurement_unit=measurement_unit
        )
        if created:
            print(f'Added ingredient: {name} ({measurement_unit})')
        else:
            print(f'Ingredient already exists: {name} ({measurement_unit})')
