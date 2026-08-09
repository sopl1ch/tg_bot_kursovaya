from datetime import time, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Record


async def get_or_create_user(session: AsyncSession,tg_id:int,user_name:str):
    result=await session.execute(select(User).where(User.tg_id==tg_id))
    user=result.scalar_one_or_none()
    if not user:
        user = User(tg_id=tg_id,user_name=user_name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user

def generate_time_slots():
    slots=[]
    for i in range(9,21):
        slots.append(time(i,0))
        slots.append(time(i,30))
    return slots

async def get_busy_times(session: AsyncSession,Doctor_id:int,selected_date:date):
    result=await session.execute(select(Record.time).where(Record.Doctor_id==Doctor_id,
                                                           Record.date==selected_date))
    return result.scalars().all()

async def get_free_times(session: AsyncSession,Doctor_id:int,selected_date:date):
    now=datetime.now()
    all_times=generate_time_slots()
    busy_times=await get_busy_times(session,Doctor_id,selected_date)
    free_times=[t for t in all_times if t not in busy_times]
    if selected_date == date.today():
        cur_time=now.time().replace(second=0,microsecond=0)
        free_times=[t for t in all_times if t>cur_time]
    return free_times

async def create_record(session: AsyncSession,
                        user_id:int,
                        Doctor_id:int,
                        selected_date:date,
                        selected_time:time):
    record=Record(
        user_id=user_id,
        Doctor_id=Doctor_id,
        date=selected_date,
        time=selected_time)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


def get_Doctors():
    return None


def get_Doctor_by_id():
    return None