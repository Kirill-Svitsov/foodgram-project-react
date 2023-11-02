from django.core.validators import (
    MinValueValidator,
    MaxValueValidator, RegexValidator
)
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.text import slugify

from constants import (
    MAX_LENGTH_INGREDIENT,
    MAX_LENGTH_TAG,
    MAX_LENGTH_TAG_COLOR,
    MAX_LENGTH_RECIPE,
    MIN_COOKING_TIME,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MAX_AMOUNT
)

from users.models import User


class Tag(models.Model):
    """Модель для Тегов"""
    name = models.CharField(
        max_length=MAX_LENGTH_TAG,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=MAX_LENGTH_TAG_COLOR,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно сотостоять из 7 символов, начиная с "#"',
            )
        ],
        help_text='Введите цвет в формате HEX (например, "#FF0000")',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        max_length=MAX_LENGTH_TAG,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            UniqueConstraint(
                fields=[
                    'name',
                    'slug'],
                name='unique_tag')]

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    """Модель для Ингредиентов"""
    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'], name='unique_ingredient'
            )
        ]

    def __str__(self):
        return str(self.name) + '' + str(self.measurement_unit)


class Recipe(models.Model):
    """Модель Рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/media',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Значение должно быть больше {MIN_COOKING_TIME}'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Значение должно быть меньше {MAX_COOKING_TIME}'
            )
        ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe'
            ),
        ]

    def __str__(self):
        return str(self.name)


class RecipeIngredient(models.Model):
    """
    Промежуточная модель, связывающая Рецепт
    и Ингредиент, необходима для добавления
    поля amount
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f'Количество не может быть меньше {MIN_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                message=f'Значение должно быть меньше {MAX_AMOUNT}'
            )
        ]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [
            UniqueConstraint(
                fields=[
                    'recipe',
                    'ingredient'],
                name='unique_recipe_ingredient'),
        ]

    def __str__(self):
        return (f'{self.ingredient.name}'
                f' ({self.amount} '
                f'{self.ingredient.measurement_unit})')


class UserRecipe(models.Model):
    """
    Базовая модель рецепта, с общими
    атрибутами для моделей ShoppingList
    и Favorite
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='%(class)ss'

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='%(class)ss'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} добавил {self.recipe.name}'


class Favorite(UserRecipe):
    """Модель для Избранного"""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite',
            )
        ]


class ShoppingList(UserRecipe):
    """Модель для тегов"""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe',
            )
        ]
