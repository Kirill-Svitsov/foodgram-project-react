def generate_shopping_list(ingredients_qs, shopping_list):
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
