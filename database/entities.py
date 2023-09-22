from datetime import datetime, time
from typing import List

from sqlalchemy import MetaData, Integer, String, BigInteger, DateTime, Boolean, Time, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(schema='kk_bot')


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(length=255), nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_login: Mapped[str] = mapped_column(String(length=255), nullable=True)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_leader: Mapped[bool] = mapped_column(Boolean, default=False)
    groups: Mapped[List['Group']] = relationship()


class District(Base):
    __tablename__ = 'districts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    callback: Mapped[str] = mapped_column(String(length=255), nullable=False)


class Type(Base):
    __tablename__ = 'types'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    callback: Mapped[str] = mapped_column(String(length=255), nullable=False)


class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped[str] = mapped_column(String(length=255), nullable=False)
    time: Mapped[time] = mapped_column(Time, nullable=False)
    address: Mapped[str] = mapped_column(String(length=500), nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, default=False)
    leader_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    type_id: Mapped[int] = mapped_column(ForeignKey('types.id'), nullable=False)
    group_type: Mapped['Type'] = relationship(lazy='joined')
    district_id: Mapped[int] = mapped_column(ForeignKey('districts.id'), nullable=False)
    district: Mapped['District'] = relationship(lazy='joined')
    group_leader: Mapped['User'] = relationship(back_populates='groups', lazy='joined')
