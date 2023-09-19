from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from database.repository import fetch_all_types, fetch_available_times, fetch_available_districts

find_group_callback = 'find_group'

start_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text='Подобрать группу', callback_data=find_group_callback)]],
)

cancel_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton(text='Вернуться', callback_data=find_group_callback)]],
)

send_contact_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(text='Отправить контакт', request_contact=True)]
], resize_keyboard=True, one_time_keyboard=True)


async def types_keyboard():
    types = await fetch_all_types()
    return split_list_and_create_buttons(input_list=types, is_districts=False)


async def districts_keyboard(type_callback):
    districts = await fetch_available_districts(type_callback)
    return split_list_and_create_buttons(input_list=districts, is_districts=True)


async def times_keyboard(district_callback, type_callback):
    times = await fetch_available_times(district_callback=district_callback, type_callback=type_callback)
    return split_list_and_create_buttons(input_list=times, is_districts=False)


def add_to_group_keyboard(telegram_id):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Присоединиться', callback_data=telegram_id)]]
    )


def split_list_and_create_buttons(input_list, is_districts):
    def create_button(item):
        return InlineKeyboardButton(
            text=item.title if hasattr(item, 'title') else str(item.strftime('%H:%M')),
            callback_data=f'{item.callback if hasattr(item, "callback") else str(item)}'
        )

    if is_districts:
        input_list.append(Button(title='Любой', callback='district_9999'))
    sub_lists = [input_list[i:i + 3] for i in range(0, len(input_list), 3)]
    inline_keyboard = []
    for sublist in sub_lists:
        buttons = [create_button(item) for item in sublist]
        inline_keyboard.append(buttons)
    inline_keyboard.append([InlineKeyboardButton(text='Отменить', callback_data='cancel')])
    return InlineKeyboardMarkup(inline_keyboard)


class Button:
    def __init__(self, title, callback) -> None:
        self.title = title
        self.callback = callback
