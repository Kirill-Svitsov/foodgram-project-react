import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def _create_data(self):
        with open('ingredients.json') as file:
            data = json.load(file)
            for line in data:
                name = line['name']
                measurement_unit = line['measurement_unit']
                if Ingredient.objects.filter(
                        name=name,
                        measurement_unit=measurement_unit
                ).exists():
                    continue
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit
                )

    def handle(self, *args, **options):
        self._create_data()
