import csv

from recipes import models

with open('ingredients.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        name, measurement_unit = row[0].split(',')
        ingredient, created = models.Ingredient.objects.get_or_create(
            name=name.strip(),
            measurement_unit=measurement_unit.strip()
        )
