from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu():
    keyboard = [
        [KeyboardButton(text="Записаться")],
        [KeyboardButton(text="Мои записи")],
        [KeyboardButton(text="Отменить запись")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)