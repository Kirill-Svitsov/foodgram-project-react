from django.db.models import Sum

from recipes.models import RecipeIngredient


def generate_shopping_list(shopping_list):
    ingredients_qs = RecipeIngredient.objects.filter(
        recipe__in=shopping_list.values('recipe')
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        amount=Sum('amount')
    ).order_by('ingredient__name')

    shopping_list_text = 'Вы выбрали следующие рецепты:\n\n'
    for item in shopping_list:
        shopping_list_text += f'- {item.recipe.name}\n'

    shopping_list_text += '\nСписок покупок:\n\n'
    for ingredient in ingredients_qs:
        shopping_list_text += (
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]})\n'
        )

    shopping_list_text += '\nПриятного аппетита!'

    return shopping_list_text
