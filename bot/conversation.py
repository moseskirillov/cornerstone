from datetime import datetime

from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes, CallbackQueryHandler

from bot.keyboards import (
    districts_keyboard,
    start_keyboard,
    FIND_GROUP_CALLBACK,
    types_keyboard,
    times_keyboard,
    add_to_group_keyboard,
    cancel_keyboard,
)
from database.repository import fetch_groups_by_params, fetch_available_times

DISTRICT, TIME, RESULT = range(3)


def conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(conversation_start, FIND_GROUP_CALLBACK)],
        states={
            DISTRICT: [CallbackQueryHandler(conversation_district, r"type_\d+")],
            TIME: [CallbackQueryHandler(conversation_time, r"district_\d+")],
            RESULT: [CallbackQueryHandler(conversation_result, r"\d+:\d+:\d+")],
        },
        fallbacks=[CallbackQueryHandler(conversation_cancel, "cancel")],
        allow_reentry=True,
    )


async def conversation_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("user_id")
    await update.callback_query.answer()
    if user_id:
        await update.callback_query.answer()
        keyboard = await types_keyboard()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нажмите на кнопку, чтобы выбрать тип",
            reply_markup=keyboard,
        )
        return DISTRICT
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы не залогинены. Для логина, сначала нажмите /start",
        )


async def conversation_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("user_id")
    await update.callback_query.answer()
    if user_id:
        type_callback = update.callback_query.data
        context.chat_data["type_callback"] = type_callback
        keyboard = await districts_keyboard(type_callback)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нажмите на кнопку, чтобы выбрать район",
            reply_markup=keyboard,
        )
        return TIME
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы не залогинены. Для логина, сначала нажмите /start",
        )


async def conversation_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("user_id")
    await update.callback_query.answer()
    if user_id:
        district_callback = update.callback_query.data
        context.chat_data["district_callback"] = district_callback
        type_callback = context.chat_data["type_callback"]
        keyboard = await times_keyboard(district_callback, type_callback)
        times = await fetch_available_times(district_callback, type_callback)
        if len(times) == 1:
            selected_groups = await fetch_groups_by_params(
                district_callback, type_callback, None
            )
            await send_groups_list(update, context, selected_groups)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Для нового поиска нажмте кнопку внизу",
                reply_markup=cancel_keyboard,
            )
            return ConversationHandler.END
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нажмите на кнопку, чтобы выбрать время",
            reply_markup=keyboard,
        )
        return RESULT
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы не залогинены. Для логина, сначала нажмите /start",
        )


async def conversation_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("user_id")
    await update.callback_query.answer()
    if user_id:
        district_callback = context.chat_data["district_callback"]
        type_callback = context.chat_data["type_callback"]
        time_callback = datetime.strptime(update.callback_query.data, "%H:%M:%S").time()
        selected_groups = await fetch_groups_by_params(
            district_callback, type_callback, time_callback
        )
        await send_groups_list(update, context, selected_groups)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Для нового поиска нажмте кнопку внизу",
            reply_markup=cancel_keyboard,
        )
        return ConversationHandler.END
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы не залогинены. Для логина, сначала нажмите /start",
        )


async def conversation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data.get("user_id")
    await update.callback_query.answer()
    if user_id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Привет, {update.effective_chat.first_name}!\n"
            f"Чтобы найти домашнюю группу, нажмите на кнопку внизу",
            reply_markup=start_keyboard,
        )
        return ConversationHandler.END
    else:
        await update.callback_query.answer()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы не залогинены. Для логина, сначала нажмите /start",
        )


async def send_groups_list(update, context, selected_groups):
    for group in selected_groups:
        keyword = add_to_group_keyboard(group.group_leader.telegram_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Район - {group.district.title}\n"
            f"Тип - {group.group_type.title}\n"
            f'Время - {str(group.time.strftime("%H:%M"))}\n'
            f"Адрес - {group.address}\n"
            f"Пастор - {group.group_leader.first_name} {group.group_leader.last_name}",
            reply_markup=keyword,
        )
