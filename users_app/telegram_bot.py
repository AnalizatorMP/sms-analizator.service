import random
import string
import time
import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, connections
from django.db.utils import OperationalError
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes, MessageHandler, filters
)

from users_app.models import TelegramChats, User

# Настройка logger
logger = logging.getLogger(__name__)


def generate_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def clean_phone_number(phone_number):
    return phone_number.lstrip('+')


@sync_to_async
def check_chat_exists(user, chat_id, max_retries=3):
    """
    Проверяет существование чата с retry-механизмом.
    
    Args:
        user: User object
        chat_id: ID чата
        max_retries: Максимальное количество попыток (по умолчанию 3)
    
    Returns:
        bool: True если чат существует, False если нет
    """
    for attempt in range(max_retries):
        try:
            # Принудительно закрываем все соединения перед новой попыткой
            connections.close_all()
            
            # Убеждаемся, что новое соединение активно
            connection.ensure_connection()
            
            # Логируем попытку
            logger.info(f"Checking chat existence attempt {attempt + 1} for chat_id: {chat_id}")
            
            # Выполняем запрос
            result = TelegramChats.objects.filter(user=user, chat_id=chat_id).exists()
            
            # Логируем успешное выполнение
            logger.info(f"Chat existence check successful for chat_id: {chat_id}, result: {result}")
            return result
            
        except OperationalError as e:
            error_code = getattr(e, 'args', [None])[0]
            
            # Проверяем, что это именно ошибки потерянного соединения
            if error_code in [2006, 2013] and attempt < max_retries - 1:
                logger.warning(
                    f"DB connection lost (error {error_code}), retry {attempt + 1}/{max_retries} "
                    f"for chat_id: {chat_id}"
                )
                
                # Exponential backoff: 1s, 2s, 3s
                sleep_time = 1 * (attempt + 1)
                time.sleep(sleep_time)
                continue
            else:
                # Если это другая ошибка или закончились попытки
                logger.error(f"DB error after {attempt + 1} attempts: {e}")
                raise
                
        except Exception as e:
            # Логируем неожиданные ошибки
            logger.error(f"Unexpected DB error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            raise
    
    # Эта строка никогда не должна выполниться, но для безопасности
    return False


@sync_to_async
def create_telegram_chat(user, title, chat_id, max_retries=3):
    """
    Создает новый чат в базе данных с retry-механизмом.
    
    Args:
        user: User object
        title: Название чата
        chat_id: ID чата
        max_retries: Максимальное количество попыток (по умолчанию 3)
    
    Returns:
        TelegramChats object созданного чата
    """
    for attempt in range(max_retries):
        try:
            # Принудительно закрываем все соединения перед новой попыткой
            connections.close_all()
            
            # Убеждаемся, что новое соединение активно
            connection.ensure_connection()
            
            # Логируем попытку
            logger.info(f"Creating telegram chat attempt {attempt + 1} for chat_id: {chat_id}")
            
            # Выполняем создание
            result = TelegramChats.objects.create(
                user=user,
                title=title,
                chat_id=chat_id
            )
            
            # Логируем успешное выполнение
            logger.info(f"Telegram chat created successfully for chat_id: {chat_id}")
            return result
            
        except OperationalError as e:
            error_code = getattr(e, 'args', [None])[0]
            
            # Проверяем, что это именно ошибки потерянного соединения
            if error_code in [2006, 2013] and attempt < max_retries - 1:
                logger.warning(
                    f"DB connection lost (error {error_code}), retry {attempt + 1}/{max_retries} "
                    f"for chat_id: {chat_id}"
                )
                
                # Exponential backoff: 1s, 2s, 3s
                sleep_time = 1 * (attempt + 1)
                time.sleep(sleep_time)
                continue
            else:
                # Если это другая ошибка или закончились попытки
                logger.error(f"DB error after {attempt + 1} attempts: {e}")
                raise
                
        except Exception as e:
            # Логируем неожиданные ошибки
            logger.error(f"Unexpected DB error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            raise
    
    # Эта строка никогда не должна выполниться, но для безопасности
    return None


@sync_to_async
def create_user(phone, telegram_id, password, max_retries=3):
    """
    Создает нового пользователя с retry-механизмом.
    
    Args:
        phone: Номер телефона пользователя
        telegram_id: ID пользователя в Telegram
        password: Пароль для пользователя
        max_retries: Максимальное количество попыток (по умолчанию 3)
    
    Returns:
        User object созданного пользователя
    """
    User = get_user_model()
    phone = clean_phone_number(phone)
    
    for attempt in range(max_retries):
        try:
            # Принудительно закрываем все соединения перед новой попыткой
            connections.close_all()
            
            # Убеждаемся, что новое соединение активно
            connection.ensure_connection()
            
            # Логируем попытку
            logger.info(f"Creating user attempt {attempt + 1} for phone: {phone}")
            
            # Выполняем создание пользователя
            new_user = User(
                email=f'{phone}@example.com',
                phone=phone,
                telegram_id=telegram_id,
                balance=0,
            )
            new_user.set_password(password)
            new_user.save()
            
            # Логируем успешное выполнение
            logger.info(f"Создан новый пользователь: {phone} (TG ID: {telegram_id})")
            return new_user
            
        except OperationalError as e:
            error_code = getattr(e, 'args', [None])[0]
            
            # Проверяем, что это именно ошибки потерянного соединения
            if error_code in [2006, 2013] and attempt < max_retries - 1:
                logger.warning(
                    f"DB connection lost (error {error_code}), retry {attempt + 1}/{max_retries} "
                    f"for user creation: {phone}"
                )
                
                # Exponential backoff: 1s, 2s, 3s
                sleep_time = 1 * (attempt + 1)
                time.sleep(sleep_time)
                continue
            else:
                # Если это другая ошибка или закончились попытки
                logger.error(f"DB error after {attempt + 1} attempts: {e}")
                raise
                
        except Exception as e:
            # Логируем неожиданные ошибки
            logger.error(f"Unexpected DB error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            raise
    
    # Эта строка никогда не должна выполниться, но для безопасности
    return None


@sync_to_async
def get_existing_user_by_telegram_id(telegram_id, max_retries=3):
    """
    Получает пользователя по telegram_id с retry-механизмом.
    
    Args:
        telegram_id: ID пользователя в Telegram
        max_retries: Максимальное количество попыток (по умолчанию 3)
    
    Returns:
        User object или None
    """
    User = get_user_model()
    
    for attempt in range(max_retries):
        try:
            # Принудительно закрываем все соединения перед новой попыткой
            connections.close_all()
            
            # Убеждаемся, что новое соединение активно
            connection.ensure_connection()
            
            # Логируем попытку подключения
            logger.info(f"DB query attempt {attempt + 1} for telegram_id: {telegram_id}")
            
            # Выполняем запрос
            result = User.objects.filter(telegram_id=telegram_id).first()
            
            # Логируем успешное выполнение
            logger.info(f"DB query successful for telegram_id: {telegram_id}")
            return result
            
        except OperationalError as e:
            error_code = getattr(e, 'args', [None])[0]
            
            # Проверяем, что это именно ошибки потерянного соединения
            if error_code in [2006, 2013] and attempt < max_retries - 1:
                logger.warning(
                    f"DB connection lost (error {error_code}), retry {attempt + 1}/{max_retries} "
                    f"for telegram_id: {telegram_id}"
                )
                
                # Exponential backoff: 1s, 2s, 3s
                sleep_time = 1 * (attempt + 1)
                time.sleep(sleep_time)
                continue
            else:
                # Если это другая ошибка или закончились попытки
                logger.error(f"DB error after {attempt + 1} attempts: {e}")
                raise
                
        except Exception as e:
            # Логируем неожиданные ошибки
            logger.error(f"Unexpected DB error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            raise
    
    # Эта строка никогда не должна выполниться, но для безопасности
    return None


@sync_to_async
def get_existing_user_by_phone(phone, max_retries=3):
    """
    Получает пользователя по номеру телефона с retry-механизмом.
    
    Args:
        phone: Номер телефона пользователя
        max_retries: Максимальное количество попыток (по умолчанию 3)
    
    Returns:
        User object или None
    """
    User = get_user_model()
    phone = clean_phone_number(phone)
    
    for attempt in range(max_retries):
        try:
            # Принудительно закрываем все соединения перед новой попыткой
            connections.close_all()
            
            # Убеждаемся, что новое соединение активно
            connection.ensure_connection()
            
            # Логируем попытку подключения
            logger.info(f"DB query attempt {attempt + 1} for phone: {phone}")
            
            # Выполняем запрос
            result = User.objects.filter(phone=phone).first()
            
            # Логируем успешное выполнение
            logger.info(f"DB query successful for phone: {phone}")
            return result
            
        except OperationalError as e:
            error_code = getattr(e, 'args', [None])[0]
            
            # Проверяем, что это именно ошибки потерянного соединения
            if error_code in [2006, 2013] and attempt < max_retries - 1:
                logger.warning(
                    f"DB connection lost (error {error_code}), retry {attempt + 1}/{max_retries} "
                    f"for phone: {phone}"
                )
                
                # Exponential backoff: 1s, 2s, 3s
                sleep_time = 1 * (attempt + 1)
                time.sleep(sleep_time)
                continue
            else:
                # Если это другая ошибка или закончились попытки
                logger.error(f"DB error after {attempt + 1} attempts: {e}")
                raise
                
        except Exception as e:
            # Логируем неожиданные ошибки
            logger.error(f"Unexpected DB error on attempt {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            raise
    
    # Эта строка никогда не должна выполниться, но для безопасности
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /start.
    Для private чатов выполняет регистрацию, для остальных — добавление группы.
    """
    # Проверяем тип чата
    chat_type = update.message.chat.type
    telegram_id = str(update.message.from_user.id)
    username = update.message.from_user.username or "Unknown"
    
    logger.info(f"START: команда /start от пользователя {telegram_id} ({username}), тип чата: {chat_type}")

    if chat_type == "private":
        logger.info(f"START: обработка приватного чата для {telegram_id}")
        
        # Для личных сообщений выполняем функционал регистрации
        contact_keyboard = KeyboardButton(text="Отправить номер телефона", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            'Нажмите кнопку ниже, чтобы отправить ваш номер телефона:',
            reply_markup=reply_markup
        )
        
        logger.info(f"START: отправлен запрос контакта пользователю {telegram_id}")
    else:
        logger.info(f"START: обработка группового чата для {telegram_id}")
        
        # Для групп/каналов выполняем функционал добавления группы
        # Проверяем, существует ли пользователь с этим Telegram ID
        logger.info(f"START: поиск пользователя по telegram_id {telegram_id}")
        
        existing_user = await get_existing_user_by_telegram_id(telegram_id)

        if existing_user:
            logger.info(f"START: пользователь найден для {telegram_id}")
            
            chat_id = update.message.chat_id
            chat_title = update.message.chat.title or "Без названия"

            logger.info(f"START: проверка существования чата {chat_id} для пользователя {telegram_id}")
            
            # Проверяем, добавлен ли этот чат ранее (используем надежную функцию с retry)
            chat_exists = await check_chat_exists(existing_user, chat_id)

            if chat_exists:
                logger.info(f"START: чат {chat_id} уже существует для пользователя {telegram_id}")
                
                await update.message.reply_text("Этот чат уже добавлен.")
            else:
                logger.info(f"START: создание нового чата {chat_id} ({chat_title}) для пользователя {telegram_id}")
                
                # Сохраняем новый чат в базе (используем надежную функцию с retry)
                await create_telegram_chat(
                    user=existing_user,
                    title=chat_title,
                    chat_id=chat_id
                )
                
                await update.message.reply_text(
                    f"Чат '{chat_title}' успешно добавлен в вашу учетную запись."
                )
                
                logger.info(f"START: чат {chat_id} ({chat_title}) успешно добавлен для пользователя {telegram_id}")
        else:
            logger.warning(f"START: пользователь НЕ найден для telegram_id {telegram_id}")
            
            # Если Telegram ID не найден, уведомляем пользователя
            await update.message.reply_text(
                "Ваш Telegram ID не зарегистрирован в системе. "
                "Пожалуйста, зарегистрируйтесь перед добавлением группы."
            )
            
            logger.info(f"START: отправлено уведомление о незарегистрированном пользователе {telegram_id}")
    
    logger.info(f"START: команда завершена для пользователя {telegram_id}")


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_contact = update.message.contact
    phone = user_contact.phone_number
    telegram_id = str(update.message.from_user.id)
    username = update.message.from_user.username or "Unknown"
    
    logger.info(f"CONTACT: получен контакт от {telegram_id} ({username}), телефон: {phone}")

    existing_user = await get_existing_user_by_telegram_id(telegram_id)
    if not existing_user:
        logger.info(f"CONTACT: проверка существования пользователя по телефону {phone}")
        
        existing_user_by_phone = await get_existing_user_by_phone(phone)

        if not existing_user_by_phone:
            logger.info(f"CONTACT: создание нового пользователя для {phone}")
            
            password = generate_password()
            new_user = await create_user(phone, telegram_id, password)

            await update.message.reply_text(f"Регистрация завершена!\n"
                                            f"Ваш пароль: {password}\n"
                                            f"Личный кабинет: https://sms.analizator.mp/login/")
            
            logger.info(f"CONTACT: пользователь {phone} успешно зарегистрирован")
        else:
            logger.warning(f"CONTACT: телефон {phone} уже зарегистрирован")
            
            await update.message.reply_text("Этот номер телефона уже зарегистрирован.")
    else:
        logger.warning(f"CONTACT: telegram_id {telegram_id} уже зарегистрирован")
        
        await update.message.reply_text("Этот Telegram ID уже зарегистрирован.")


def main():
    logger.info("Запуск Telegram бота...")
    try:
        app = ApplicationBuilder().token(settings.TOKEN_BOT).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

        logger.info("Telegram бот запущен и готов к работе")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка запуска Telegram бота: {e}")
        raise


if __name__ == '__main__':
    main()
