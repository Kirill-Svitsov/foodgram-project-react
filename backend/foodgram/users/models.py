from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint

from constants import (
    MAX_LENGTH_USER_EMAIL,
    MAX_LENGTH_USER_FIELD
)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(
        unique=True,
        max_length=MAX_LENGTH_USER_EMAIL,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_USER_FIELD,
        unique=True,
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIELD,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_USER_FIELD,
        verbose_name='Фамилия'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'), ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user.username} -> {self.author.username}"
