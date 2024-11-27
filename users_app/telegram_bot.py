import random
import string

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes, MessageHandler, filters
)

from users_app.models import TelegramChats, User


# Обработчик полученного контакта
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


def clean_phone_number(phone_number):
    return phone_number.lstrip('+')


@sync_to_async
def create_user(phone, telegram_id, password):
    User = get_user_model()
    phone = clean_phone_number(phone)
    new_user = User(
        email=f'{phone}@example.com',
        phone=phone,
        telegram_id=telegram_id,
        balance=0,
    )
    new_user.set_password(password)
    new_user.save()
    return new_user


@sync_to_async
def get_existing_user_by_telegram_id(telegram_id):
    User = get_user_model()
    return User.objects.filter(telegram_id=telegram_id).first()


@sync_to_async
def get_existing_user_by_phone(phone):
    User = get_user_model()
    phone = clean_phone_number(phone)
    return User.objects.filter(phone=phone).first()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает команду /start.
    Для private чатов выполняет регистрацию, для остальных — добавление группы.
    """
    # Проверяем тип чата
    chat_type = update.message.chat.type

    if chat_type == "private":
        # Для личных сообщений выполняем функционал регистрации
        contact_keyboard = KeyboardButton(text="Отправить номер телефона", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            'Нажмите кнопку ниже, чтобы отправить ваш номер телефона:',
            reply_markup=reply_markup
        )
    else:
        # Для групп/каналов выполняем функционал добавления группы
        telegram_id = str(update.message.from_user.id)

        # Проверяем, существует ли пользователь с этим Telegram ID
        existing_user = await get_existing_user_by_telegram_id(telegram_id)

        if existing_user:
            chat_id = update.message.chat_id
            chat_title = update.message.chat.title or "Без названия"

            # Проверяем, добавлен ли этот чат ранее
            existing_chat_query = TelegramChats.objects.filter(user=existing_user, chat_id=chat_id)
            chat_exists = await sync_to_async(existing_chat_query.exists)()

            if chat_exists:
                await update.message.reply_text("Этот чат уже добавлен.")
            else:
                # Сохраняем новый чат в базе
                await sync_to_async(TelegramChats.objects.create)(
                    user=existing_user,
                    title=chat_title,
                    chat_id=chat_id
                )
                await update.message.reply_text(
                    f"Чат '{chat_title}' успешно добавлен в вашу учетную запись."
                )
        else:
            # Если Telegram ID не найден, уведомляем пользователя
            await update.message.reply_text(
                "Ваш Telegram ID не зарегистрирован в системе. "
                "Пожалуйста, зарегистрируйтесь перед добавлением группы."
            )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_contact = update.message.contact
    phone = user_contact.phone_number
    telegram_id = str(update.message.from_user.id)

    existing_user = await get_existing_user_by_telegram_id(telegram_id)
    if not existing_user:
        existing_user_by_phone = await get_existing_user_by_phone(phone)

        if not existing_user_by_phone:
            password = generate_password()

            new_user = await create_user(phone, telegram_id, password)

            await update.message.reply_text(f"Регистрация завершена!\n"
                                            f"Ваш пароль: {password}\n"
                                            f"Личный кабинет: https://sms.analizator.mp/login/")
        else:
            await update.message.reply_text("Этот номер телефона уже зарегистрирован.")
    else:
        await update.message.reply_text("Этот Telegram ID уже зарегистрирован.")


def main():
    app = ApplicationBuilder().token(settings.TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
