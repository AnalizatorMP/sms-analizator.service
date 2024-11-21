from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes, MessageHandler, filters
)

from users_app.models import TelegramChats, User


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пожалуйста, введите ваш email для авторизации:"
    )
    context.user_data['awaiting_email'] = True


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_email'):
        return

    email = update.message.text.strip()
    user_query = User.objects.filter(email=email)
    user_exists = await sync_to_async(user_query.exists)()

    if not user_exists:
        await update.message.reply_text(
            "Пользователь с таким email не найден. Введите email снова."
        )
        return

    user = await sync_to_async(user_query.first)()

    chat_id = update.message.chat_id
    chat_title = update.message.chat.title or "Без названия"

    existing_chat_query = TelegramChats.objects.filter(user=user, chat_id=chat_id)
    chat_exists = await sync_to_async(existing_chat_query.exists)()

    if chat_exists:
        await update.message.reply_text(
            f"Этот чат уже добавлен для пользователя {user.email}."
        )
    else:
        await sync_to_async(TelegramChats.objects.create)(
            user=user,
            title=chat_title,
            chat_id=chat_id
        )

        await update.message.reply_text(
            f"Авторизация прошла успешно! Чат '{chat_title}' добавлен в вашу учетную запись."
        )

    context.user_data.pop('awaiting_email', None)


def main():
    app = ApplicationBuilder().token(settings.TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
