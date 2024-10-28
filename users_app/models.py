from django.db import models
from django.contrib.auth.models import AbstractUser

from users_app.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    balance = models.IntegerField(
        default=0,
        verbose_name='Баланс'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email}'
