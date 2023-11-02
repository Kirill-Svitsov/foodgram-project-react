import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def _create_data(self):
        if os.path.exists('ingredients.json'):
            with open('ingredients.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                counter = 0
                for line in data:
                    name = line['name']
                    measurement_unit = line['measurement_unit']
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    if created:
                        counter += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                (f'Created Ingredient: {name},'
                                 f' общее количество: {counter}')
                            )
                        )
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Файл ingredients.json не существует'
                )
            )

    def _load_tags(self):
        tags_data = [
            {
                'name': 'Завтрак',
                'color': '#FF0000',
                'slug': 'zavtrak'
            },
            {
                'name': 'Обед',
                'color': '#00FF00',
                'slug': 'obed'
            },
            {
                'name': 'Ужин',
                'color': '#0000FF',
                'slug': 'uzhin'
            },
        ]
        counter = 0
        for tag_info in tags_data:
            tag, created = Tag.objects.get_or_create(**tag_info)
            if created:
                counter += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        (f'Created Tag: {tag.name},'
                         f' общее количество: {counter}')
                    )
                )

    def handle(self, *args, **options):
        self._create_data()
        self._load_tags()
