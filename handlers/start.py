import os

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import get_or_create_user
from keyboards.menu import main_menu

load_dotenv()

router = Router()
@router.message(CommandStart())
async def command_start(message: Message, session:AsyncSession, is_admin=None):
    await get_or_create_user(
        session=session,
        tg_id=message.from_user.id,
        user_name=message.from_user.username or message.from_user.full_name
    )
    await message.answer("Добро пожаловать в бот записи к врачу",
                         reply_markup=main_menu(is_admin=is_admin))