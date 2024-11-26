import secrets

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, password=None, **extra_fields):
        # Генерация токена, если не задан
        if 'token_url' not in extra_fields or not extra_fields['token_url']:
            extra_fields['token_url'] = secrets.token_urlsafe(32)

        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(password, **extra_fields)
