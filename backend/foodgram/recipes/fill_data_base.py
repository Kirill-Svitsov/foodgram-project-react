import csv

from models import Ingredient

with open('../api/commands/ingredients.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        name, measurement_unit = row[0].split(',')
        ingredient, created = Ingredient.objects.get_or_create(
            name=name.strip(),
            measurement_unit=measurement_unit.strip()
        )
