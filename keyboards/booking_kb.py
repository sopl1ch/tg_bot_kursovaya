from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import time


def Doctors_keyboard(Doctors):
    return InlineKeyboardMarkup(
        inline_keyboard=[
           [ InlineKeyboardButton(text=Doctor.name, callback_data=f"Doctor:{Doctor.id}")]
            for Doctor in Doctors
        ]
    )
def times_keyboard(free_times:list[time]):
    keyboard=[
        [InlineKeyboardButton(text=t.strftime("%H:%M"), callback_data=f"time:{t.strftime('%H:%M')}")]
        for t in free_times
    ]
    keyboard.append([InlineKeyboardButton(text="Назад к календарю",callback_data="back_to_calendar")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

router=Router
