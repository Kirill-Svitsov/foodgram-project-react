# praktikum_new_diplom
Список эндпоинтов:
- Пользователи:
```
http://localhost/api/users/
```
- Тэги:
```
http://localhost/api/tags/
```
- Рецепты:
```
http://localhost/api/recipes/
```
Пример POST запроса на создание рецепта:
```
{
  "name": "Тестовый рецепт на ингридиенты по ид",
  "text": "Очень вкусный греческий салат",
  "cooking_time": 15,
  "ingredients": [
    {"ingredient": 1, "amount": 2},
    {"ingredient": 2, "amount": 2},
    {"ingredient": 3, "amount": 4}
  ],
  "tags": [1, 2]
}
```
- Скачать список покупок:
```
http://localhost/api/recipes/download_shopping_cart/
```
- Избранное:
```
http://localhost/api/recipes/{id}/favorite/
```
- Список подписок:
```
http://localhost/api/users/subscriptions/
```
- Ингредиенты:
```
http://localhost/api/ingredients/
```
Суперюзер:
```
Логин: Svitsov
Пароль: cuprumelement29
```