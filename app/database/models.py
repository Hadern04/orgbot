from sqlalchemy import String, BigInteger, Integer, Date, ForeignKey, Boolean
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)

    # Связи
    events: Mapped[list['Event']] = relationship(back_populates='user')
    managed_chats: Mapped[list['Chat']] = relationship(back_populates='manager')
    owned_contractors: Mapped[List['Contractor']] = relationship(back_populates='owner')
    accessible_contractors: Mapped[List['ContractorAccess']] = relationship(back_populates='user')


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[Date] = mapped_column(Date, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    # Связь с пользователем
    user: Mapped['User'] = relationship(back_populates='events')


class Contractor(Base):
    __tablename__ = 'contractors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact: Mapped[str] = mapped_column(String, nullable=True)

    # Владелец подрядчика
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    owner: Mapped['User'] = relationship(back_populates='owned_contractors')

    # Пользователи с доступом к этому подрядчику
    shared_with: Mapped[List['ContractorAccess']] = relationship(back_populates='contractor')


class ContractorAccess(Base):
    __tablename__ = 'contractor_access'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contractor_id: Mapped[int] = mapped_column(Integer, ForeignKey('contractors.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    contractor: Mapped['Contractor'] = relationship(back_populates='shared_with')
    user: Mapped['User'] = relationship()


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    id_user: Mapped[int] = mapped_column(Integer, nullable=False)
    manager_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    # Связи
    manager: Mapped['User'] = relationship(back_populates='managed_chats')
