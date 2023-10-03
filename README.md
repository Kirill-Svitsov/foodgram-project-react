# praktikum_new_diplom
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