from calendar import monthrange
from datetime import date, time

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from db.requests import get_doctors, get_free_times, get_or_create_user, create_record, get_user_records, delete_record
from keyboards.booking_kb import doctors_keyboard, times_keyboard
from states.booking_state import BookingState

router = Router()

@router.message(F.text == "Записаться")
async def start_booking_from_menu(message: Message, state: FSMContext, session: AsyncSession):
    doctors = await get_doctors(session)
    if not doctors:
        await message.answer("В базе данных нет врачей.")
        return
    await state.clear()
    await state.set_state(BookingState.choosing_Doctor)
    await message.answer("Выберите врача:", reply_markup=doctors_keyboard(doctors))

@router.callback_query(StateFilter(BookingState.choosing_Doctor), F.data.startswith("doctor:"))
async def choose_doctor(callback: CallbackQuery, state: FSMContext):
    doctor_id = int(callback.data.split(":")[1])
    await state.update_data(doctor_id=doctor_id)
    await state.set_state(BookingState.choosing_date)
    today = date.today()
    await callback.answer()
    await callback.message.answer("Выберите дату:", reply_markup=get_calendar(today.year, today.month))

@router.callback_query(StateFilter(BookingState.choosing_date), F.data == "ignore")
async def ignore_calendar(callback: CallbackQuery):
    await callback.answer()

def get_calendar(year, month):
    months = [
        "Январь", "Февраль", "Март", "Апрель",
        "Май", "Июнь", "Июль", "Август",
        "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    keyboard = [
        [InlineKeyboardButton(text=f"{months[month - 1]} {year}", callback_data="ignore")],
        [
            InlineKeyboardButton(text="Пн", callback_data="ignore"),
            InlineKeyboardButton(text="Вт", callback_data="ignore"),
            InlineKeyboardButton(text="Ср", callback_data="ignore"),
            InlineKeyboardButton(text="Чт", callback_data="ignore"),
            InlineKeyboardButton(text="Пт", callback_data="ignore"),
            InlineKeyboardButton(text="Сб", callback_data="ignore"),
            InlineKeyboardButton(text="Вс", callback_data="ignore")
        ]
    ]

    first_weekday, days_in_month = monthrange(year, month)
    row = []

    for _ in range(first_weekday):
        row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day in range(1, days_in_month + 1):
        row.append(
            InlineKeyboardButton(
                text=str(day),
                callback_data=f"cal_day.{year}.{month}.{day}"
            )
        )
        if len(row) == 7:
            keyboard.append(row)
            row = []

    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(text="<", callback_data=f"cal_prev.{year}.{month}"),
        InlineKeyboardButton(text=">", callback_data=f"cal_next.{year}.{month}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(StateFilter(BookingState.choosing_date), F.data.startswith("cal_prev."))
async def prev_calendar(callback: CallbackQuery):
    _, year, month = callback.data.split(".")
    year, month = int(year), int(month)
    month -= 1

    if month == 0:
        month = 12
        year -= 1

    today = date.today()

    if (year, month) < (today.year, today.month):
        await callback.answer("Нельзя выбрать прошлый месяц.", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=get_calendar(year, month))
    await callback.answer()

@router.callback_query(StateFilter(BookingState.choosing_date), F.data.startswith("cal_next."))
async def next_calendar(callback: CallbackQuery):
    _, year, month = callback.data.split(".")
    year, month = int(year), int(month)
    month += 1

    if month == 13:
        month = 1
        year += 1

    await callback.message.edit_reply_markup(reply_markup=get_calendar(year, month))
    await callback.answer()

@router.callback_query(StateFilter(BookingState.choosing_date), F.data.startswith("cal_day."))
async def choose_date(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    _, year, month, day = callback.data.split(".")
    selected_date = date(int(year), int(month), int(day))

    if selected_date < date.today():
        await callback.answer("Нельзя выбрать прошедшую дату.", show_alert=True)
        return

    data = await state.get_data()
    doctor_id = data["doctor_id"]
    free_times = await get_free_times(session, doctor_id, selected_date)

    if not free_times:
        await callback.answer("На эту дату нет свободного времени.", show_alert=True)
        return

    await state.update_data(selected_date=selected_date.isoformat())
    await state.set_state(BookingState.choosing_time)

    await callback.message.answer(
        f"Дата: {selected_date.strftime('%d.%m.%Y')}\nВыберите время:",
        reply_markup=times_keyboard(free_times)
    )
    await callback.answer()

@router.callback_query(StateFilter(BookingState.choosing_time), F.data == "back_to_calendar")
async def back_to_calendar(callback: CallbackQuery, state: FSMContext):
    today = date.today()
    await state.set_state(BookingState.choosing_date)
    await callback.message.answer("Выберите дату:", reply_markup=get_calendar(today.year, today.month))
    await callback.answer()

@router.callback_query(StateFilter(BookingState.choosing_time), F.data.startswith("time:"))
async def choose_time(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    _, hour, minute = callback.data.split(":")
    selected_time = time(int(hour), int(minute))

    data = await state.get_data()
    doctor_id = data["doctor_id"]
    selected_date = date.fromisoformat(data["selected_date"])

    user_name = callback.from_user.username or callback.from_user.full_name

    user = await get_or_create_user(
        session=session,
        tg_id=callback.from_user.id,
        user_name=user_name)
    record = await create_record(
        session=session,
        user_id=user.id,
        Doctor_id=doctor_id,
        selected_date=selected_date,
        selected_time=selected_time)

    await callback.message.edit_text(
        "Вы успешно записаны!\n\n"
        f"Номер записи: {record.id}\n"
        f"Дата: {selected_date.strftime('%d.%m.%Y')}\n"
        f"Время: {selected_time.strftime('%H:%M')}")

    await state.clear()


@router.message(F.text == "Отменить запись")
async def show_records_for_cancel(message: Message, session: AsyncSession):
    user = await get_or_create_user(
        session=session,
        tg_id=message.from_user.id,
        user_name=message.from_user.username or message.from_user.full_name
    )

    records = await get_user_records(session, user.id)

    if not records:
        await message.answer("У вас нет записей для отмены.")
        return

    keyboard = []

    for record, doctor_name in records:
        text = (f"{doctor_name} — "
            f"{record.date.strftime('%d.%m.%Y')} "
            f"{record.time.strftime('%H:%M')}")
        keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"cancel:{record.id}")])
    await message.answer(
        "Выберите запись для отмены:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard))
@router.callback_query(F.data.startswith("cancel:"))
async def cancel_booking(
    callback: CallbackQuery,
    session: AsyncSession
):
    record_id = int(callback.data.split(":")[1])

    user = await get_or_create_user(
        session=session,
        tg_id=callback.from_user.id,
        user_name=callback.from_user.username or callback.from_user.full_name)

    deleted = await delete_record(
        session=session,
        record_id=record_id,
        user_id=user.id)
    if not deleted:
        await callback.answer(
            "Запись не найдена или уже отменена.",
            show_alert=True)
        return
    await callback.message.edit_text(
        "Запись отменена.")
    await callback.answer()


@router.message(F.text == "Мои записи")
async def show_my_records(message: Message, session: AsyncSession):
    user = await get_or_create_user(
        session=session,
        tg_id=message.from_user.id,
        user_name=message.from_user.username or message.from_user.full_name
    )

    records = await get_user_records(
        session,
        user.id
    )

    if not records:
        await message.answer("У вас пока нет записей.")
        return

    text = "Ваши записи:\n\n"

    for record, doctor_name in records:
        text += (
            f"Врач: {doctor_name}\n"
            f"Дата: {record.date.strftime('%d.%m.%Y')}\n"
            f"Время: {record.time.strftime('%H:%M')}\n"
            f"№ записи: {record.id}\n\n"
        )

    await message.answer(text)