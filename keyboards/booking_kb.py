from datetime import time

from aiogram import Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
def doctors_keyboard(doctors):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                    text=doctor.name,
                    callback_data=f"doctor:{doctor.id}",)]
            for doctor in doctors])
def times_keyboard(free_times: list[time]):
    keyboard = [
        [InlineKeyboardButton(
                text=t.strftime("%H:%M"),
                callback_data=f"time:{t.strftime('%H:%M')}",)]
        for t in free_times]
    keyboard.append(
        [InlineKeyboardButton(
                text="Назад к календарю",
                callback_data="back_to_calendar",)])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )