from datetime import date,time

import cur
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Date, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base

class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    tg_id:Mapped[int]=mapped_column(BigInteger,unique=True)
    user_name:Mapped[str]=mapped_column(String(100))
    role:Mapped[str]=mapped_column(String(20),default='user')

    records: Mapped[list["Record"]] = relationship(back_populates="user")
class Doctor(Base):
    __tablename__='Doctors'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100),unique=True)

    records:Mapped[list["Record"]]=relationship(back_populates="Doctor")

class Record(Base):
    __tablename__='records'
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    Doctor_id:Mapped[int]=mapped_column(ForeignKey('Doctors.id'))
    date:Mapped[date]=mapped_column(Date)
    time:Mapped[time]=mapped_column(Time)
    __table_args__=(UniqueConstraint("Doctor_id","date","time",name="uq_Doctor_date_time"),)




