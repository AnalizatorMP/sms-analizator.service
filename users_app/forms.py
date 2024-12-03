import re

from django import forms
from django.core.exceptions import ValidationError

from users_app.models import KEY_TYPES, NumbersService, TelegramChats


class ServiceForm(forms.Form):
    sender = forms.CharField(max_length=255, label="Отправитель")

    # Это поле будет содержать номер телефона, выбранный пользователем
    telephone = forms.ModelChoiceField(
        queryset=NumbersService.objects.none(),
        label='Телефон',
        empty_label='Выберите телефон'
    )

    # Это поле будет содержать канал Telegram, выбранный пользователем
    telegram_chat = forms.ModelChoiceField(
        queryset=TelegramChats.objects.none(),
        label='Канал Telegram',
        empty_label='Выберите канал Telegram'
    )

    any_sender = forms.BooleanField(required=False, label="Любой отправитель")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Ограничиваем выборы только данными для конкретного пользователя
            self.fields['telephone'].queryset = NumbersService.objects.filter(user=user)
            self.fields['telegram_chat'].queryset = TelegramChats.objects.filter(user=user)


class ServiceKeyForm(forms.Form):
    service = forms.ChoiceField(
        choices=[('', 'Выберите сервис')] + list(KEY_TYPES),
        label='Сервис'
    )
    name = forms.CharField(max_length=255, label="Название")
    key = forms.CharField(max_length=255, label="Ключ", required=False)
    telephone = forms.CharField(max_length=100, label="Номер телефона", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        service = self.data.get('service')
        if service == 'Novofon':
            self.fields['telephone'].required = True  # Делаем поле телефон обязательным для Novofon
        else:
            self.fields['telephone'].required = False  # Иначе оно не обязательно

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '').strip()

        # Убираем все нецифровые символы
        telephone = re.sub(r'\D', '', telephone)

        # Проверяем, что номер начинается с 7 и состоит из 11 цифр
        if len(telephone) != 11 or not telephone.startswith('7'):
            raise ValidationError('Номер телефона должен быть в формате 7XXXXXXXXXX (11 цифр, начинающихся с 7).')

        return telephone
