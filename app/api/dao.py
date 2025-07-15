from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from app.api.base import BaseDAO
from app.database.models import User, Event, Contractor, Chat, ContractorAccess
from app.database.db import async_session_maker


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_one_with_events(cls, telegram_id: int):
        """Находит пользователя по telegram_id и сразу загружает связанные с ним события."""
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(telegram_id=telegram_id)
                .options(selectinload(cls.model.events))
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()


class EventDAO(BaseDAO):
    model = Event

    @classmethod
    async def get_events_by_user(cls, user_id: int):
        """
        Возвращает все мероприятия пользователя по user_id.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Список мероприятий пользователя.
        """
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model)
                    .filter_by(user_id=user_id)
                    .order_by(cls.model.event_date)
                )
                result = await session.execute(query)
                events = result.scalars().all()

                return [
                    {
                        "event_id": event.id,
                        "event_title": event.title,
                        "event_date": event.event_date,
                        "event_location": event.location,
                        "user_id": event.user_id
                    }
                    for event in events
                ]
            except SQLAlchemyError as e:
                print(f"Error while fetching events for user {user_id}: {e}")
                return None


class ContractorDAO(BaseDAO):
    model = Contractor

    @classmethod
    async def get_all_categories(cls) -> list[str]:
        """Возвращает список всех уникальных категорий подрядчиков."""
        async with async_session_maker() as session:
            query = select(cls.model.category).distinct()
            result = await session.execute(query)
            return [row[0] for row in result.all()]

    @classmethod
    async def get_contractors_by_user(cls, user_id: int):
        """
        Возвращает всех подрядчиков пользователя по user_id.

        Аргументы:
            user_id: Идентификатор пользователя (владельца).

        Возвращает:
            Список подрядчиков пользователя.
        """
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model)
                    .filter_by(owner_id=user_id)
                    .order_by(cls.model.name)
                )
                result = await session.execute(query)
                contractors = result.scalars().all()

                return [
                    {
                        "id": contractor.id,
                        "name": contractor.name,
                        "category": contractor.category,
                        "contact": contractor.contact,
                        "owner_id": contractor.owner_id
                    }
                    for contractor in contractors
                ]
            except SQLAlchemyError as e:
                print(f"Error while fetching contractors for user {user_id}: {e}")
                return None

    @classmethod
    async def get_shared_contractors(cls, user_id: int):
        """
        Возвращает подрядчиков, к которым пользователь имеет доступ.

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Список подрядчиков с информацией о правах доступа.
        """
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model, ContractorAccess.can_edit)
                    .join(ContractorAccess, cls.model.id == ContractorAccess.contractor_id)
                    .filter(ContractorAccess.user_id == user_id)
                    .order_by(cls.model.name)
                )
                result = await session.execute(query)

                return [
                    {
                        "id": contractor.id,
                        "name": contractor.name,
                        "category": contractor.category,
                        "contact": contractor.contact,
                        "owner_id": contractor.owner_id,
                        "can_edit": can_edit
                    }
                    for contractor, can_edit in result.all()
                ]
            except SQLAlchemyError as e:
                print(f"Error while fetching shared contractors for user {user_id}: {e}")
                return None

    @classmethod
    async def get_all_accessible_contractors(cls, user_id: int):
        """
        Возвращает всех подрядчиков, доступных пользователю
        (как собственных, так и расшаренных).

        Аргументы:
            user_id: Идентификатор пользователя.

        Возвращает:
            Объединенный список подрядчиков.
        """
        try:
            owned = await cls.get_contractors_by_user(user_id) or []
            shared = await cls.get_shared_contractors(user_id) or []

            # Объединяем списки, убирая возможные дубликаты
            contractors_dict = {c["id"]: c for c in owned + shared}
            return list(contractors_dict.values())

        except Exception as e:
            print(f"Error while fetching all accessible contractors: {e}")
            return None


class ChatDAO(BaseDAO):
    model = Chat
