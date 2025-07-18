from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete
from app.database.db import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            data_id: Критерии фильтрации в виде идентификатора записи.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """
        Асинхронно находит и возвращает один экземпляр модели по указанным критериям или None.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Экземпляр модели или None, если ничего не найдено.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        """
        Асинхронно находит и возвращает все экземпляры модели, удовлетворяющие указанным критериям.

        Аргументы:
            **filter_by: Критерии фильтрации в виде именованных параметров.

        Возвращает:
            Список экземпляров модели.
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **values):
        """
        Асинхронно создает новый экземпляр модели с указанными значениями.

        Аргументы:
            **values: Именованные параметры для создания нового экземпляра модели.

        Возвращает:
            Созданный экземпляр модели.
        """
        async with async_session_maker() as session:
            new_instance = cls.model(**values)
            session.add(new_instance)
            try:
                await session.commit()
                await session.refresh(new_instance)
                return new_instance
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    @classmethod
    async def delete(cls, id: int):
        """
        Асинхронно удаляет экземпляр модели по ID.

        Аргументы:
            id: ID удаляемого экземпляра.

        Возвращает:
            True если удаление прошло успешно, False если запись не найдена.
        """
        async with async_session_maker() as session:
            async with session.begin():
                result = await session.execute(delete(cls.model).where(cls.model.id == id))
                if result.rowcount == 0:
                    return False
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return True

    @classmethod
    async def update(cls, id: int, **values):
        """
        Асинхронно обновляет экземпляр модели по ID.

        Аргументы:
            id: ID обновляемого экземпляра.
            **values: Поля для обновления.

        Возвращает:
            Обновленный экземпляр модели или None если запись не найдена.
        """
        async with async_session_maker() as session:
            async with session.begin():
                # Проверяем существование записи
                existing = await session.get(cls.model, id)
                if not existing:
                    return None

                # Обновляем поля
                stmt = (
                    update(cls.model)
                    .where(cls.model.id == id)
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                try:
                    await session.execute(stmt)

                    # Обновляем объект в сессии
                    await session.refresh(existing)
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e

            return existing
