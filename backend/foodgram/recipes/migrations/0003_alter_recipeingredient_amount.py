# Generated by Django 4.2.5 on 2023-10-11 17:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_recipe_pub_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Количество не может быть меньше 1')], verbose_name='Количество'),
        ),
    ]
