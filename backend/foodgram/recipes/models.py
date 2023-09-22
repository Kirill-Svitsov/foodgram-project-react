from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)  # Хранение цвета в формате HEX (#RRGGBB)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    description = models.TextField()
    cooking_time = models.PositiveIntegerField()
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount} {self.ingredient.unit})"


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.title}"


class ShoppingList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shopping_list')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.title}"


class Follow(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"{self.user.username} -> {self.author.username}"
