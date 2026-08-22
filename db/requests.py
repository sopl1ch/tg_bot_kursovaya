from datetime import time, date, datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Record, Doctor

async def get_doctors(session: AsyncSession):
    result = await session.execute(select(Doctor))
    return result.scalars().all()

async def get_or_create_user(session: AsyncSession, tg_id: int, user_name: str):
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(tg_id=tg_id, user_name=user_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user

def generate_time_slots():
    slots = []
    for i in range(9, 21):
        slots.append(time(i, 0))
        slots.append(time(i, 30))
    return slots

async def get_busy_times(session: AsyncSession, Doctor_id: int, selected_date: date):
    result = await session.execute(
        select(Record.time).where(
            Record.Doctor_id == Doctor_id,
            Record.date == selected_date
        )
    )
    return result.scalars().all()

async def get_free_times(session: AsyncSession, Doctor_id: int, selected_date: date):
    now = datetime.now()
    all_times = generate_time_slots()
    busy_times = await get_busy_times(session, Doctor_id, selected_date)
    free_times = [t for t in all_times if t not in busy_times]
    if selected_date == date.today():
        current_time = now.time().replace(second=0, microsecond=0)
        free_times = [t for t in free_times if t > current_time]
    return free_times

async def create_record(session: AsyncSession, user_id: int, Doctor_id: int, selected_date: date, selected_time: time):
    record = Record(
        user_id=user_id,
        Doctor_id=Doctor_id,
        date=selected_date,
        time=selected_time
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def get_user_records(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Record, Doctor.name)
        .join(Doctor, Doctor.id == Record.Doctor_id)
        .where(Record.user_id == user_id)
        .order_by(Record.date, Record.time)
    )
    return result.all()

async def delete_record(session: AsyncSession, record_id: int, user_id: int):
    result = await session.execute(
        select(Record).where(
            Record.id == record_id,
            Record.user_id == user_id
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        return False

    await session.delete(record)
    await session.commit()
    return True



