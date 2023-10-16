import re

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.db.models import UniqueConstraint

from users.models import CustomUser


def validate_hex_color(value):
    pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Неверный формат ввода. Цвет должен быть в HEX формате: #FFFFFF"
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        validators=[validate_hex_color],
        verbose_name="Цвет",
    )
    slug = models.SlugField(
        unique=True,
        max_length=150,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        constraints = [
            UniqueConstraint(
                fields=[
                    "name",
                    "slug"],
                name="unique_tag")]

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_ingredient"
            )
        ]

    def __str__(self):
        return str(self.name) + " " + str(self.measurement_unit)


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/media',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    is_favorited = models.BooleanField(
        default=False,
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='В списке покупок'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            UniqueConstraint(fields=["name", "author"], name="unique_recipe"),
        ]

    def __str__(self):
        return str(self.name)

    def get_image_url(self):
        return self.image.url if self.image else None


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        "Количество",
        validators=[MinValueValidator(1, "Количество не может быть меньше 1")],
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Количество ингредиента в рецепте"
        constraints = [
            UniqueConstraint(
                fields=[
                    "recipe",
                    "ingredient"],
                name="unique_recipe_ingredient"),
        ]

    def __str__(self):
        return (f"{self.ingredient.name}"
                f" ({self.amount} "
                f"{self.ingredient.measurement_unit})")


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.name}"
