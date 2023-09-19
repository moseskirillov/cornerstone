import asyncio
import logging
import os
from asyncio import AbstractEventLoop

from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from bot.handlers import start_handler, select_district_handler, select_type_handler, select_time_handler, \
    select_groups_handler, send_user_contact_handler, send_add_request_handler, error_handler
from bot.keyboards import find_group_callback
from database.connection import database_init

TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def handlers_register(application: Application) -> None:
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('cancel', start_handler))
    application.add_handler(CallbackQueryHandler(start_handler, 'cancel'))
    application.add_handler(CallbackQueryHandler(select_type_handler, find_group_callback))
    application.add_handler(CallbackQueryHandler(select_district_handler, r'type_\d+'))
    application.add_handler(CallbackQueryHandler(select_time_handler, r'district_\d+'))
    application.add_handler(CallbackQueryHandler(select_groups_handler, r'\d+:\d+:\d+'))
    application.add_handler(CallbackQueryHandler(send_user_contact_handler, r'\d+'))
    application.add_handler(MessageHandler(filters.CONTACT, send_add_request_handler))
    application.add_error_handler(error_handler)


def main() -> None:
    application: Application = ApplicationBuilder().token(TOKEN).build()
    handlers_register(application)
    application.run_webhook(
        listen=os.getenv('LISTEN'),
        port=int(os.getenv('PORT')),
        url_path='',
        webhook_url=os.getenv('URL'),
    )


if __name__ == '__main__':
    loop: AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(database_init())
    main()
