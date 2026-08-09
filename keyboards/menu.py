from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu(is_admin=False):
    keyboard=[
        [InlineKeyboardButton(text="Записаться",callback_data="start_booking")],
        [InlineKeyboardButton(text="Мои записи",callback_data="my_records")],
        [InlineKeyboardButton(text="Отменить запись",callback_data="cancel_record_menu")]

    ]