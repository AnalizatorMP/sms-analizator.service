import secrets

from django.db import models
from django.contrib.auth.models import AbstractUser

from users_app.managers import UserManager

KEY_TYPES = (
    ('Novofon', 'Novofon'),
    ('Telfin', 'Telfin'),
    ('Mango', 'Mango')
)


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
    token_url = models.CharField(
        max_length=500,
        verbose_name='Токен для Вебхука',
        null=True,
        blank=True
    )
    telegram_id = models.CharField(
        max_length=500,
        verbose_name='ID TG',
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=100,
        null=True,
        verbose_name='Телефон',
        unique=True
    )
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.phone}'

    def save(self, *args, **kwargs):
        if not self.token_url:
            self.token_url = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class Key(models.Model):
    name = models.CharField(max_length=50, choices=KEY_TYPES, verbose_name='Тип ключа')
    title = models.TextField(
        verbose_name='Название кабинета',
        null=True,
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='key')
    token = models.CharField(max_length=1000, verbose_name='Токен')

    class Meta:
        verbose_name = 'Ключ'
        verbose_name_plural = 'Ключи'

    def __str__(self):
        return f'{self.title}'


class TelegramChats(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    title = models.TextField(
        verbose_name='Название канала'
    )
    chat_id = models.CharField(
        max_length=250,
        verbose_name='ID чата ТГ'
    )

    class Meta:
        verbose_name = 'ТГ канал'
        verbose_name_plural = 'ТГ каналы'

    def __str__(self):
        return f'{self.title}'


class NumbersService(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    name = models.CharField(
        max_length=50,
        choices=KEY_TYPES,
        verbose_name='Сервис'
    )
    telephone = models.CharField(
        max_length=100,
        verbose_name='Номер телефона',
        unique=True
    )

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'

    def __str__(self):
        return f'{self.name} - {self.telephone}'


class Rules(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    sender = models.CharField(
        max_length=1000,
        verbose_name='Отравитель'
    )
    from_whom = models.ForeignKey(
        NumbersService,
        on_delete=models.CASCADE,
        verbose_name='От кого'
    )
    to_whom = models.ForeignKey(
        TelegramChats,
        on_delete=models.CASCADE,
        verbose_name='Куда'
    )

    class Meta:
        verbose_name = 'Правило'
        verbose_name_plural = 'Правила'

    def __str__(self):
        return f'{self.user}'
