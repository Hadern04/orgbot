from datetime import datetime
from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.api.base import BaseDAO
from app.database.db import async_session_maker
from app.database.models import User, Event, Contractor, ContractorCategory, Task, ChecklistItem, Checklist, \
    EventChecklist, EventContractor, CompletedChecklistItem


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def find_one_with_events(cls, telegram_id: int):
        """Находит пользователя по telegram_id и сразу загружает связанные с ним события."""
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.telegram_id == telegram_id)
                .options(selectinload(cls.model.events))
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()


class EventDAO(BaseDAO):
    model = Event

    @classmethod
    async def get_events_by_user(cls, owner_id: int):
        """Возвращает все мероприятия пользователя"""
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model)
                    .where(cls.model.owner_id == owner_id)
                    .order_by(cls.model.date)
                )
                result = await session.execute(query)
                events = result.scalars().all()

                return [
                    {
                        "id": event.id,
                        "title": event.title,
                        "date": event.date,
                        "location": event.location,
                        "owner_id": event.owner_id
                    }
                    for event in events
                ]
            except SQLAlchemyError as e:
                print(f"Error fetching events for user {owner_id}: {e}")
                return None

    @classmethod
    async def get_event_with_details(cls, event_id: int):
        """Возвращает мероприятие со всеми связанными данными"""
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.id == event_id)
                .options(
                    selectinload(cls.model.tasks),
                    selectinload(cls.model.contractors_link).joinedload(EventContractor.contractor),
                    selectinload(cls.model.checklists_link).joinedload(EventChecklist.checklist),
                    selectinload(cls.model.completed_items).joinedload(CompletedChecklistItem.item)
                )
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def assign_contractor(cls, event_id: int, contractor_id: int, cost: str):
        """Назначение подрядчика с указанием стоимости"""
        async with async_session_maker() as session:
            assignment = EventContractor(
                event_id=event_id,
                contractor_id=contractor_id,
                cost=cost
            )
            session.add(assignment)
            await session.commit()


class ContractorDAO(BaseDAO):
    model = Contractor

    @classmethod
    async def get_categories_by_user(cls, owner_id: int) -> list[dict[str, Any]]:
        """Возвращает уникальные категории подрядчиков пользователя"""
        async with async_session_maker() as session:
            query = (
                select(ContractorCategory.id, ContractorCategory.title)
                .where(ContractorCategory.owner_id == owner_id)
                .distinct()
            )
            result = await session.execute(query)
            return [
                {
                    "id": row[0],
                    "title": row[1]
                }
                for row in result.all()]

    @classmethod
    async def get_contractors_by_user(cls, owner_id: int):
        """Возвращает подрядчиков пользователя с категориями"""
        async with async_session_maker() as session:
            try:
                query = (
                    select(cls.model, ContractorCategory.title)
                    .join(ContractorCategory, cls.model.category_id == ContractorCategory.id)
                    .where(cls.model.owner_id == owner_id)
                    .order_by(cls.model.name)
                )
                result = await session.execute(query)

                return [
                    {
                        "id": contractor.id,
                        "name": contractor.name,
                        "category": category_title,
                        "contact": contractor.contact,
                        "owner_id": contractor.owner_id
                    }
                    for contractor, category_title in result.all()
                ]
            except SQLAlchemyError as e:
                print(f"Error fetching contractors for user {owner_id}: {e}")
                return None

    @classmethod
    async def get_contractors_for_event(cls, event_id: int):
        """Возвращает подрядчиков для конкретного мероприятия"""
        async with async_session_maker() as session:
            query = (
                select(EventContractor, Contractor)
                .join(Contractor, EventContractor.contractor_id == Contractor.id)
                .where(EventContractor.event_id == event_id)
            )
            result = await session.execute(query)

            return [
                {
                    "id": contractor.id,
                    "name": contractor.name,
                    "contact": contractor.contact,
                    "cost": event_contractor.cost
                }
                for event_contractor, contractor in result.all()
            ]


class ContractorCategoryDAO(BaseDAO):
    model = ContractorCategory


class ChecklistDAO(BaseDAO):
    model = Checklist

    @classmethod
    async def get_checklists_for_event(cls, event_id: int):
        """Возвращает чек-листы для мероприятия со статусом выполнения"""
        async with async_session_maker() as session:
            query = (
                select(EventChecklist, Checklist)
                .join(Checklist, EventChecklist.checklist_id == Checklist.id)
                .where(EventChecklist.event_id == event_id)
            )
            result = await session.execute(query)

            return [
                {
                    "id": checklist.id,
                    "title": checklist.title,
                    "is_completed": event_checklist.is_completed,
                    "completed_at": event_checklist.completed_at
                }
                for event_checklist, checklist in result.all()
            ]

    @classmethod
    async def create_template(cls, owner_id: int, title: str, items: list[str]):
        """Создание шаблона чек-листа с пунктами"""
        async with async_session_maker() as session:
            checklist = await cls.add(
                owner_id=owner_id,
                title=title,
                is_template=True
            )

            if items:
                items_instances = [
                    ChecklistItem(
                        checklist_id=checklist.id,
                        title=item_text
                    )
                    for item_text in items
                ]
                session.add_all(items_instances)

            await session.commit()
            return checklist

    @classmethod
    async def assign_to_event(cls, checklist_id: int, event_id: int):
        """Привязка чек-листа к мероприятию"""
        async with async_session_maker() as session:
            assignment = EventChecklist(
                event_id=event_id,
                checklist_id=checklist_id
            )
            session.add(assignment)
            await session.commit()

    @classmethod
    async def mark_item_completed(cls, event_id: int, item_id: int, user_id: int):
        """Отметка пункта как выполненного"""
        async with async_session_maker() as session:
            # Проверяем существование записи
            query = (
                select(CompletedChecklistItem)
                .where(CompletedChecklistItem.event_id == event_id)
                .where(CompletedChecklistItem.item_id == item_id)
            )
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                existing.is_completed = True
                existing.completed_at = datetime.now()
                existing.completed_by = user_id
            else:
                new_completion = CompletedChecklistItem(
                    event_id=event_id,
                    item_id=item_id,
                    is_completed=True,
                    completed_at=datetime.now(),
                    completed_by=user_id
                )
                session.add(new_completion)

            await session.commit()


class TaskDAO(BaseDAO):
    model = Task

    @classmethod
    async def get_tasks_for_event(cls, event_id: int):
        """Возвращает задачи для мероприятия"""
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .where(cls.model.event_id == event_id)
                .order_by(cls.model.date)
            )
            result = await session.execute(query)

            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "date": task.date,
                    "status": task.status
                }
                for task in result.scalars()
            ]


class ChecklistItemDAO(BaseDAO):
    model = ChecklistItem

    @classmethod
    async def get_completed_items_for_event(cls, event_id: int):
        """Возвращает выполненные пункты для мероприятия"""
        async with async_session_maker() as session:
            query = (
                select(CompletedChecklistItem, ChecklistItem)
                .join(ChecklistItem, CompletedChecklistItem.item_id == ChecklistItem.id)
                .where(CompletedChecklistItem.event_id == event_id)
            )
            result = await session.execute(query)

            return [
                {
                    "id": item.id,
                    "title": item.title,
                    "is_completed": completed_item.is_completed,
                    "completed_at": completed_item.completed_at
                }
                for completed_item, item in result.all()
            ]

    @classmethod
    async def delete_all_for_checklist(cls, checklist_id: int) -> int:
        """Удаляет все пункты чек-листа (без удаления отметок о выполнении)"""
        async with async_session_maker() as session:
            delete_stmt = (
                delete(EventChecklist)
                .where(EventChecklist.checklist_id == checklist_id)
            )
            result = await session.execute(delete_stmt)
            await session.commit()

            return result.rowcount
