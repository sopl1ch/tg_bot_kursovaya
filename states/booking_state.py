from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    choosing_Doctor = None
    choosing_lesson=State()
    choosing_date=State()
    choosing_time=State()