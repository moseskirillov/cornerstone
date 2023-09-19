from datetime import datetime

from sqlalchemy import select, insert

from database.connection import async_session
from database.entities import District, Group, Type, User
from database.models import CreateUserRequest


async def create_or_update_user(request: CreateUserRequest):
    async with async_session() as session:
        async with session.begin():
            row = await session.execute(
                select(User)
                .where(User.telegram_id == request.telegram_id)
            )
            user = row.scalar_one_or_none()
            if user:
                user.last_login = datetime.now()
            else:
                await session.execute(insert(User), [{
                    'first_name': request.first_name,
                    'last_name': request.last_name,
                    'telegram_login': request.telegram_login,
                    'telegram_id': request.telegram_id
                }])


async def fetch_all_types():
    async with async_session() as session:
        async with session.begin():
            rows = await session.execute(
                select(Group)
                .where(Group.is_open)
                .join(Type)
                .distinct(Type.title)
            )
            groups = rows.scalars().all()
            return [group.group_type for group in groups]


async def fetch_available_districts(type_callback):
    async with async_session() as session:
        async with session.begin():
            rows = await session.execute(
                select(Group)
                .where(Group.is_open)
                .where(Type.callback == type_callback)
                .join(District)
                .join(Type)
                .distinct(District.title)
            )
            groups = rows.scalars().all()
            return [group.district for group in groups]


async def fetch_available_times(district_callback, type_callback):
    async with async_session() as session:
        async with session.begin():
            if district_callback == 'district_9999':
                rows = await session.execute(
                    select(Group.time)
                    .distinct()
                    .where(Group.is_open)
                    .where(Type.callback == type_callback)
                    .join(Type)
                    .join(District)
                )
            else:
                rows = await session.execute(
                    select(Group.time)
                    .distinct()
                    .where(Group.is_open)
                    .where(District.callback == district_callback)
                    .where(Type.callback == type_callback)
                    .join(Type)
                    .join(District)
                )
            times = rows.scalars().all()
            return times


async def fetch_groups_by_params(district_callback, type_callback, selected_time):
    async with async_session() as session:
        async with session.begin():
            if district_callback == 'district_9999':
                rows = await session.execute(
                    select(Group)
                    .where(Type.callback == type_callback)
                    .where(Group.time == selected_time)
                    .where(Group.is_open)
                    .join(Type)
                    .join(District)
                    .join(User)
                )
            else:
                rows = await session.execute(
                    select(Group)
                    .where(District.callback == district_callback)
                    .where(Type.callback == type_callback)
                    .where(Group.time == selected_time)
                    .where(Group.is_open)
                    .join(Type)
                    .join(District)
                    .join(User)
                )
            groups = rows.scalars().fetchall()
            return groups


async def fetch_leader_name_by_telegram(telegram_id):
    async with async_session() as session:
        async with session.begin():
            row = await session.execute(
                select(User)
                .where(User.telegram_id == int(telegram_id))
            )
            user = row.scalar_one()
            return user
