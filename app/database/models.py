from datetime import date
from typing import List, Optional

from sqlalchemy import String, BigInteger, Integer, Date, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Связи
    events: Mapped[List['Event']] = relationship(back_populates='owner')
    contractors: Mapped[List['Contractor']] = relationship(back_populates='owner')
    categories: Mapped[List['ContractorCategory']] = relationship(back_populates='owner')
    checklists: Mapped[List['Checklist']] = relationship(back_populates='owner')


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Связи
    owner: Mapped['User'] = relationship(back_populates='events')
    tasks: Mapped[List['Task']] = relationship(back_populates='event', cascade='all, delete-orphan')
    contractors_link: Mapped[List['EventContractor']] = relationship(back_populates='event')
    checklists_link: Mapped[List['EventChecklist']] = relationship(back_populates='event')
    completed_items: Mapped[List['CompletedChecklistItem']] = relationship(back_populates='event')


class ContractorCategory(Base):
    __tablename__ = 'contractor_categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)

    # Связи
    owner: Mapped['User'] = relationship(back_populates='categories')
    contractors: Mapped[List['Contractor']] = relationship(back_populates='category')


class Contractor(Base):
    __tablename__ = 'contractors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('contractor_categories.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact: Mapped[str] = mapped_column(String(200), nullable=False)

    # Связи
    owner: Mapped['User'] = relationship(back_populates='contractors')
    category: Mapped['ContractorCategory'] = relationship(back_populates='contractors')
    events_link: Mapped[List['EventContractor']] = relationship(back_populates='contractor')


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Связи
    event: Mapped['Event'] = relationship(back_populates='tasks')


class ChecklistItem(Base):
    __tablename__ = 'checklist_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Связи
    completions: Mapped[List['CompletedChecklistItem']] = relationship(back_populates='item')


class Checklist(Base):
    __tablename__ = 'checklists'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Связи
    owner: Mapped['User'] = relationship(back_populates='checklists')
    events_link: Mapped[List['EventChecklist']] = relationship(back_populates='checklist')


class EventContractor(Base):
    """Связь мероприятий и подрядчиков"""
    __tablename__ = 'event_contractors'

    event_id: Mapped[int] = mapped_column(
        ForeignKey('events.id', ondelete='CASCADE'),
        primary_key=True
    )
    contractor_id: Mapped[int] = mapped_column(
        ForeignKey('contractors.id', ondelete='CASCADE'),
        primary_key=True
    )
    cost: Mapped[Optional[str]] = mapped_column(String)

    # Связи
    event: Mapped['Event'] = relationship(back_populates='contractors_link')
    contractor: Mapped['Contractor'] = relationship(back_populates='events_link')


class EventChecklist(Base):
    """Связь мероприятий и чек-листов"""
    __tablename__ = 'event_checklists'

    event_id: Mapped[int] = mapped_column(
        ForeignKey('events.id', ondelete='CASCADE'),
        primary_key=True
    )
    checklist_id: Mapped[int] = mapped_column(
        ForeignKey('checklists.id', ondelete='CASCADE'),
        primary_key=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[date]] = mapped_column(Date)

    # Связи
    event: Mapped['Event'] = relationship(back_populates='checklists_link')
    checklist: Mapped['Checklist'] = relationship(back_populates='events_link')


class CompletedChecklistItem(Base):
    __tablename__ = 'completed_checklist_items'

    event_id: Mapped[int] = mapped_column(
        ForeignKey('events.id', ondelete='CASCADE'),
        primary_key=True
    )
    item_id: Mapped[int] = mapped_column(
        ForeignKey('checklist_items.id', ondelete='CASCADE'),
        primary_key=True
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[date]] = mapped_column(Date)
    completed_by: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))

    # Связи
    event: Mapped['Event'] = relationship(back_populates='completed_items')
    item: Mapped['ChecklistItem'] = relationship(back_populates='completions')
    user: Mapped[Optional['User']] = relationship()
