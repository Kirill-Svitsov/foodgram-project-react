[![Main foodgram workflow](https://github.com/Kirill-Svitsov/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Kirill-Svitsov/foodgram-project-react/actions/workflows/main.yml)

# Foodgram graduation project by Kirill Svitsov

## Description

Это дипломный проект, завершающий мое обучение в Яндекс.Практикум.
«Фудграм» — сайт, на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Пользователям сайта также будет доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Technologies

- Python 3.10
- Django 4.2.4
- Django Rest Framework
- Docker
- React
- SPA
- Nginx

## Запустить проект локально:

- Установите и активируйте виртуальное окружение

```
  python3 -m venv venv
```

```
  source venv/bin/activate
```

- Установите зависимости из файла requirements.txt

```
  pip install -r requirements.txt
```

- Выполните миграции из папки с файлом manage.py

```
  python3 manage.py makemigtations
```

```
  python3 manage.py migrate
```
- Для локальных тестов необходимо заполнить БД командой:
```
  python3 manage.py fill_data_base
```
## Список основных эндпоинтов:

- Пользователи:

```
http://localhost/api/users/
```

- Для авторизованного пользователя есть возможность просмотра своего профиля

```
http://localhost/api/users/me/
```

- Тэги:

```
http://localhost/api/tags/
```

- Рецепты:

```
http://localhost/api/recipes/
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

Superuser:

```
Логин: Svitsov
Пароль: cuprumelement29
```