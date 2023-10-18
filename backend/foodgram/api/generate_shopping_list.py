def generate_shopping_list(shopping_list):
    ingredients_dict = {}
    for item in shopping_list:
        recipe = item.recipe
        for ri in recipe.recipeingredient_set.all():
            ingredient_name = ri.ingredient.name
            ingredient_unit = ri.ingredient.measurement_unit
            amount = ri.amount
            if (ingredient_name, ingredient_unit) in ingredients_dict:
                ingredients_dict[(ingredient_name, ingredient_unit)] += amount
            else:
                ingredients_dict[(ingredient_name, ingredient_unit)] = amount

    shopping_list_text = "Вы выбрали следующие рецепты:\n\n"
    for item in shopping_list:
        shopping_list_text += f"- {item.recipe.name}\n"

    shopping_list_text += "\nСписок покупок:\n\n"
    for (ingredient_name, ingredient_unit), amount in ingredients_dict.items():
        shopping_list_text += f"{ingredient_name} ({amount} {ingredient_unit})\n"

    shopping_list_text += "\nПриятного аппетита!"

    return shopping_list_text
