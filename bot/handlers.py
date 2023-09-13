import html
import json
import logging
import textwrap
import traceback
from datetime import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.keyboards import start_keyboard, districts_keyboard, types_keyboard, times_keyboard, add_to_group_keyboard, \
    send_contact_keyboard, cancel_keyboard
from database.models import CreateUserRequest
from database.repository import fetch_groups_by_params, fetch_leader_name_by_telegram, create_or_update_user
from sheet.request import AddRequest
from sheet.sheet_service import add_join_request


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await create_or_update_user(CreateUserRequest(
        first_name=update.effective_chat.first_name,
        last_name=update.effective_chat.last_name or None,
        telegram_id=update.effective_chat.id
    ))
    context.user_data['user_id'] = update.effective_chat.id
    if update.callback_query:
        await update.callback_query.answer()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Привет, {update.effective_chat.first_name}!\n'
             f'Чтобы найти домашнюю группу, нажмите на кнопку внизу',
        reply_markup=start_keyboard
    )


async def select_district_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.user_data.get('user_id')
    if user_id:
        await update.callback_query.answer()
        keyboard = await districts_keyboard()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нажмите на кнопку, чтобы выбрать район',
            reply_markup=keyboard
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не залогинены. Для логина, сначала нажмите /start'
        )


async def select_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.user_data.get('user_id')
    if user_id:
        await update.callback_query.answer()
        district_callback = update.callback_query.data
        context.chat_data['district_callback'] = district_callback
        keyboard = await types_keyboard(district_callback=district_callback)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нажмите на кнопку, чтобы выбрать тип',
            reply_markup=keyboard
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не залогинены. Для логина, сначала нажмите /start'
        )


async def select_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.user_data.get('user_id')
    if user_id:
        await update.callback_query.answer()
        district_callback = context.chat_data['district_callback']
        type_callback = update.callback_query.data
        context.chat_data['type_callback'] = type_callback
        keyboard = await times_keyboard(district_callback=district_callback, type_callback=type_callback)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нажмите на кнопку, чтобы выбрать время',
            reply_markup=keyboard
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не залогинены. Для логина, сначала нажмите /start'
        )


async def select_groups_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.user_data.get('user_id')
    if user_id:
        await update.callback_query.answer()
        district_callback = context.chat_data['district_callback']
        type_callback = context.chat_data['type_callback']
        time_callback = datetime.strptime(update.callback_query.data, '%H:%M:%S').time()
        selected_groups = await fetch_groups_by_params(district_callback, type_callback, time_callback)
        for group in selected_groups:
            keyword = add_to_group_keyboard(group.group_leader.telegram_id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Район - {group.district.title}\n'
                     f'Тип - {group.group_type.title}\n'
                     f'Время - {str(group.time.strftime("%H:%M"))}\n'
                     f'Адрес - {group.address}\n'
                     f'Пастор - {group.group_leader.first_name} {group.group_leader.last_name}',
                reply_markup=keyword
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Для нового поиска нажмте кнопку внизу',
            reply_markup=cancel_keyboard
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не залогинены. Для логина, сначала нажмите /start'
        )


async def send_user_contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = context.user_data.get('user_id')
    if user_id:
        await update.callback_query.answer()
        context.chat_data['leader_id'] = update.callback_query.data
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нажмите на кнопку чтобы отправить Ваш контакт и пастор домашней группы свяжется с Вами',
            reply_markup=send_contact_keyboard
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не залогинены. Для логина, сначала нажмите /start'
        )


async def send_add_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    leader_id = context.chat_data.get('leader_id')
    if leader_id:
        await context.bot.send_message(
            chat_id=leader_id,
            text='Получен новый запрос на присоединение к Вашей домашней группе. Контакт человека:'
        )
        await context.bot.send_contact(
            chat_id=leader_id,
            contact=update.effective_message.contact
        )
        leader = await fetch_leader_name_by_telegram(leader_id)
        request = AddRequest(
            date=datetime.now().strftime("%d.%m.%Y"),
            first_name=update.effective_chat.first_name,
            last_name=update.effective_chat.last_name,
            telegram=update.effective_chat.username,
            leader_name=f'{leader.first_name} {leader.last_name}',
        )
        add_join_request(request)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Спасибо, скоро с вами свяжется пастор домашней группы'
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Вы не залогинены. Для логина, сначала нажмите /start'
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error('Произошла ошибка при работе бота:', exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    wrapped_traceback = textwrap.wrap(tb_string, width=2048)
    error_message = (
        f'<pre>Произошла ошибка при работе бота\n</pre>'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
    )
    await context.bot.send_message(chat_id='1472373299', text=error_message, parse_mode=ParseMode.HTML)

    for i, part in enumerate(wrapped_traceback):
        traceback_message = f'<pre>{html.escape(part)}</pre>'
        message = f'<pre>Стек-трейс, часть {i + 1} из ' \
                  f'{len(wrapped_traceback)}</pre>\n\n' \
                  f'{traceback_message}'
        await context.bot.send_message(chat_id='1472373299', text=message, parse_mode=ParseMode.HTML)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Произошла ошибка при работе бота. Пожалуйста, нажмите /start для новой попытки или попробуйте позже',
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
