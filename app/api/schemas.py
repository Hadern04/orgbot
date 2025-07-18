from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


# Модель для валидации данных
class EventData(BaseModel):
    """Базовая схема для мероприятия"""
    title: str = Field(
        ...,
        max_length=100,
        description="Название мероприятия"
    )
    date: date = Field(
        ...,
        description="Дата проведения мероприятия"
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Место проведения мероприятия"
    )
    owner_id: int = Field(
        ...,
        description="ID пользователя")


class ContractorData(BaseModel):
    """Базовая схема для подрядчика"""
    name: str = Field(
        ...,
        max_length=100,
        description="Наименование подрядчика"
    )
    category: str = Field(
        ...,
        description="Категория подрядчика"
    )
    contact: str = Field(
        ...,
        max_length=200,
        description="Контакты подрядчика"
    )
    owner_id: str = Field(
        ...,
        description="ID создателя")