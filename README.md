# SMS Анализатор Service

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.1+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3+-purple.svg)

Профессиональный веб-сервис для анализа, обработки и автоматической пересылки SMS сообщений в Telegram каналы с поддержкой множественных SMS-провайдеров.

## 📋 Оглавление

- [Особенности](#особенности)
- [Архитектура](#архитектура)
- [Технологии](#технологии)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Использование](#использование)
- [API](#api)
- [Frontend](#frontend)
- [Структура проекта](#структура-проекта)
- [Тестирование](#тестирование)
- [Развертывание](#развертывание)
- [Безопасность](#безопасность)

## ✨ Особенности

### 🔧 Основная функциональность
- **Мультипровайдерная поддержка**: Интеграция с SMS-сервисами Novofon, Telfin, Mango
- **Умная система правил**: Гибкая настройка правил пересылки SMS по отправителям и номерам
- **Telegram интеграция**: Автоматическая пересылка SMS в указанные Telegram каналы
- **Webhook система**: Прием SMS через защищенные webhook'и
- **Многопользовательская система**: Изоляция данных между пользователями

### 🎨 Пользовательский интерфейс
- **Современный дизайн**: Адаптивный UI на Bootstrap 5 с темной/светлой темой
- **Интуитивная навигация**: Sidebar с иконками и понятной структурой
- **Мобильная адаптация**: Полная поддержка мобильных устройств
- **Rich UI компоненты**: Формы, таблицы, модальные окна, уведомления

### 🤖 Telegram Bot
- **Автоматическая регистрация**: Регистрация пользователей через Telegram
- **Управление каналами**: Добавление Telegram каналов для пересылки
- **Генерация паролей**: Автоматическое создание безопасных паролей

### 🔐 Безопасность
- **JWT авторизация**: Современная система аутентификации
- **Токенизация webhook'ов**: Защищенные эндпоинты для приема SMS
- **Валидация данных**: Комплексная проверка входящих данных
- **Логирование**: Детальное логирование всех операций

## 🏗 Архитектура

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   SMS Providers │────│  Django API  │────│ Telegram Bot    │
│ (Novofon/Telfin │    │   (Webhook)  │    │                 │
│     /Mango)     │    └──────────────┘    └─────────────────┘
└─────────────────┘           │                       │
                              │                       │
                    ┌──────────────┐           ┌─────────────┐
                    │   Frontend   │           │  Database   │
                    │  (Bootstrap) │           │   (MySQL)   │
                    └──────────────┘           └─────────────┘
```

### Компоненты системы:

1. **Web Application** - Django приложение с REST API
2. **Telegram Bot** - Бот для регистрации и управления каналами  
3. **Frontend** - Современный веб-интерфейс на Bootstrap
4. **Webhook Handler** - Обработчик входящих SMS от провайдеров
5. **Rule Engine** - Система правил для фильтрации и пересылки

## 🛠 Технологии

### Backend
- **Django 5.1.3** - Основной веб-фреймворк
- **Django REST Framework 3.15.2** - API разработка
- **MySQL 8.0+** - Основная база данных
- **python-telegram-bot 21.7** - Telegram Bot API
- **drf-yasg 1.21.8** - Swagger документация

### Frontend
- **Bootstrap 5.3** - CSS фреймворк
- **jQuery 3.6+** - JavaScript библиотека
- **ApexCharts** - Графики и диаграммы
- **DataTables** - Интерактивные таблицы
- **SweetAlert2** - Красивые уведомления

### Иконки и UI
- **Bootstrap Icons** - Основные иконки
- **FontAwesome 6** - Расширенный набор иконок
- **Material Design Icons** - Material иконки
- **Tabler Icons** - Современные SVG иконки

### Development
- **python-dotenv** - Управление конфигурацией
- **loguru** - Продвинутое логирование
- **pytest** - Тестирование

## 🚀 Установка

### Предварительные требования

```bash
- Python 3.9+
- MySQL 8.0+
- Git
- pip
- virtualenv (рекомендуется)
```

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/sms-analizator.service.git
cd sms-analizator.service
```

### 2. Создание виртуального окружения

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Создайте базу данных MySQL:

```sql
CREATE DATABASE sms_analizator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sms_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sms_analizator.* TO 'sms_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Конфигурация окружения

Создайте файл `.env` в корне проекта:

```env
# Database
DB_NAME=sms_analizator
DB_USER=sms_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Telegram Bot
TOKEN_BOT=your_telegram_bot_token

# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Миграции базы данных

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 8. Запуск сервера

```bash
# Web-сервер
python manage.py runserver

# Telegram Bot (в отдельном терминале)
python manage.py run_bot
```

## ⚙️ Конфигурация

### Настройка SMS провайдеров

#### Novofon
1. Получите API ключ в личном кабинете Novofon
2. Добавьте номер в системе через веб-интерфейс
3. Настройте webhook: `https://yourdomain.com/webhook/{user_token}/`

#### Telfin
1. Получите API ключ в кабинете Telfin  
2. Добавьте ключ через интерфейс настройки сервисов
3. Настройте webhook URL в Telfin

#### Mango
1. Получите API ключ Mango Office
2. Добавьте ключ в систему
3. Настройте webhook для SMS уведомлений

### Настройка Telegram бота

1. Создайте бота через @BotFather
2. Получите токен и добавьте в `.env`
3. Запустите команду: `python manage.py run_bot`

## 💡 Использование

### Регистрация

1. Перейдите к боту @SMS_Analizator_bot в Telegram
2. Нажмите `/start` и следуйте инструкциям
3. Отправьте контакт для регистрации
4. Получите логин и пароль

### Настройка сервисов

1. Войдите в веб-интерфейс
2. Перейдите в "Настройка сервисов"
3. Добавьте API ключи ваших SMS провайдеров
4. Для Novofon добавьте номера телефонов

### Настройка Telegram каналов

1. Добавьте бота в ваш Telegram канал как администратора
2. В боте используйте команды для добавления канала
3. Канал появится в списке доступных для правил

### Создание правил пересылки

1. Перейдите в "Настройка правил"
2. Выберите отправителя SMS (или "Любой отправитель")
3. Выберите номер телефона-получателя
4. Выберите Telegram канал для пересылки
5. Сохраните правило

### Мониторинг

SMS будут автоматически пересылаться согласно настроенным правилам. Проверьте логи для отслеживания:

```bash
tail -f logs/django.log
```

## 🔌 API

### Аутентификация

```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password"
}
```

### Webhook для SMS

```http
POST /webhook/{user_token}/
Content-Type: application/json

{
    "from": "+1234567890",
    "to": "+0987654321", 
    "text": "SMS message text",
    "sender": "SENDER"
}
```

### Документация API

После запуска сервера доступна по адресу:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## 🎨 Frontend

### Особенности интерфейса

#### Адаптивный дизайн
- Полная поддержка мобильных устройств
- Гибкая система сетки Bootstrap
- Адаптивная навигация с коллапсом

#### Современный UI/UX
- Material Design принципы
- Плавные анимации и переходы
- Интуитивные формы с валидацией
- Rich-компоненты (DataTables, Charts, Modals)

#### Темизация
- Поддержка светлой и темной темы
- Настраиваемые цветовые схемы
- Система CSS переменных

#### Компоненты
- **Навигация**: Sidebar с категориями и иконками
- **Формы**: Валидация, автокомплит, селекты
- **Таблицы**: Сортировка, фильтрация, пагинация
- **Модальные окна**: Подтверждения, формы
- **Уведомления**: Toast, SweetAlert

### Структура frontend

```
templates/
├── assets/                 # Статические ресурсы
│   ├── css/               # Стили
│   ├── js/                # JavaScript
│   ├── images/            # Изображения
│   ├── icon-fonts/        # Наборы иконок
│   └── libs/              # Внешние библиотеки
├── html/                  # HTML шаблоны
│   ├── index.html         # Главная страница
│   ├── login.html         # Авторизация
│   ├── a_my_forms.html    # Настройка правил
│   ├── a_my_input.html    # Настройка сервисов
│   └── ...                # Другие страницы
└── partials/              # Переиспользуемые части
```

## 📁 Структура проекта

```
sms-analizator.service/
├── manage.py                           # Django management
├── requirements.txt                    # Python зависимости
├── sms_analizator_service/            # Основные настройки
│   ├── __init__.py
│   ├── settings.py                    # Конфигурация Django
│   ├── urls.py                        # URL маршруты
│   ├── wsgi.py                        # WSGI application
│   └── asgi.py                        # ASGI application
├── users_app/                         # Основное приложение
│   ├── __init__.py
│   ├── models.py                      # Модели данных
│   ├── views.py                       # Контроллеры
│   ├── urls.py                        # URL маршруты
│   ├── forms.py                       # Django формы
│   ├── admin.py                       # Админ панель
│   ├── telegram_bot.py                # Telegram бот
│   ├── managers.py                    # Менеджеры моделей
│   ├── api/                           # REST API
│   │   ├── __init__.py
│   │   ├── serializers.py             # Сериализаторы
│   │   ├── urls.py                    # API маршруты
│   │   └── auth/                      # Аутентификация
│   │       ├── __init__.py
│   │       ├── views.py               # API views
│   │       └── urls.py                # Auth маршруты
│   └── management/                    # Django команды
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── run_bot.py             # Запуск бота
├── utils/                             # Утилиты
│   ├── __init__.py
│   └── novofon.py                     # Novofon интеграция
└── templates/                         # Frontend файлы
    ├── admin/                         # Django admin
    ├── assets/                        # Статика
    ├── html/                          # HTML шаблоны
    ├── drf-yasg/                      # Swagger UI
    └── rest_framework/                # DRF шаблоны
```

## 🧪 Тестирование

### Настройка тестовой среды

```bash
# Установка зависимостей для тестирования
pip install pytest pytest-django pytest-cov

# Создание тестовой базы
python manage.py migrate --settings=sms_analizator_service.test_settings
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=users_app --cov-report=html

# Конкретный модуль
pytest users_app/tests/test_models.py

# Интеграционные тесты API
pytest users_app/tests/test_api.py
```

### Ключевые тест-кейсы

1. **Модели**
   - Создание и валидация пользователей
   - Связи между моделями
   - Уникальность токенов

2. **API**
   - Аутентификация и авторизация
   - CRUD операции
   - Валидация данных

3. **Webhook**
   - Обработка входящих SMS
   - Парсинг различных форматов
   - Система правил

4. **Telegram Bot**
   - Регистрация пользователей
   - Команды бота
   - Обработка сообщений

## 🚢 Развертывание

### Production настройки

1. **Обновите настройки**:
   ```python
   # settings.py
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECURE_SSL_REDIRECT = True
   SECURE_HSTS_SECONDS = 31536000
   ```

2. **Настройте веб-сервер** (Nginx + Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn sms_analizator_service.wsgi:application
   ```

3. **Конфигурация Nginx**:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location /static/ {
           alias /path/to/your/static/files/;
       }
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker развертывание

```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "sms_analizator_service.wsgi:application"]
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to server
      run: |
        # Your deployment script
```

## 🔒 Безопасность

### Меры безопасности

1. **Аутентификация**
   - JWT токены с истечением
   - Безопасное хранение паролей (bcrypt)
   - Защита от брут-форс атак

2. **Авторизация**
   - Изоляция данных между пользователями  
   - Проверка прав доступа к ресурсам
   - Валидация webhook токенов

3. **Защита данных**
   - HTTPS обязательно в production
   - Шифрование чувствительных данных
   - Валидация и санитизация входных данных

4. **Мониторинг**
   - Логирование всех операций
   - Мониторинг подозрительной активности
   - Алерты на ошибки безопасности

### Рекомендации по безопасности

```python
# Используйте сильные пароли
SECURE_PASSWORD_VALIDATORS = [
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',
]

# Настройте CORS правильно
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]

# Используйте HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

## 📊 Мониторинг и логирование

### Настройка логирования

Система использует комплексное логирование:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'users_app': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Мониторинг метрик

- Количество обработанных SMS
- Время отклика webhook'ов
- Ошибки обработки правил
- Активность пользователей

## 🤝 Вклад в проект

### Процесс разработки

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

### Стандарты кода

- Используйте PEP 8 для Python
- Добавляйте docstrings для функций
- Покрывайте код тестами
- Обновляйте документацию

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 📞 Поддержка

- **Email**: support@example.com
- **Telegram**: @your_support_bot
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)

## 🗺 Roadmap

### Версия 2.0
- [ ] Поддержка дополнительных SMS провайдеров
- [ ] Аналитика и отчеты
- [ ] API для интеграции с внешними системами
- [ ] Мобильное приложение

### Версия 2.1
- [ ] Машинное обучение для классификации SMS
- [ ] Расширенные правила фильтрации
- [ ] Интеграция с CRM системами
- [ ] Масштабирование для enterprise

---

**Разработано с ❤️ для эффективной работы с SMS** 