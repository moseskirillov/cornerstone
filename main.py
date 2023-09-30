import asyncio
import logging
import os
from asyncio import AbstractEventLoop

from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from bot.conversation import conversation_handler
from bot.handlers import (
    error_handler,
    start_handler,
    send_user_contact_handler,
    send_add_request_handler,
)
from database.connection import database_init

TOKEN = os.getenv("BOT_TOKEN")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def handlers_register(application: Application) -> None:
    application.add_handler(conversation_handler())
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(start_handler, "cancel"))
    application.add_handler(CallbackQueryHandler(send_user_contact_handler, r"\d+"))
    application.add_handler(MessageHandler(filters.CONTACT, send_add_request_handler))
    application.add_error_handler(error_handler)


def main() -> None:
    application: Application = ApplicationBuilder().token(TOKEN).build()
    handlers_register(application)
    application.run_webhook(
        listen=os.getenv("LISTEN_ADDRESS"),
        port=os.getenv("LISTEN_PORT"),
        url_path=os.getenv("URL_PATH"),
        webhook_url=os.getenv("WEBHOOK_URL"),
    )


if __name__ == "__main__":
    loop: AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(database_init())
    main()
