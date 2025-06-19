from sqlalchemy import delete, insert, select, update
from typing import Any, Generic, Type, TypeVar, Optional, List

from src.database import get_async_session


T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Базовый репозиторий для выполнения асинхронных CRUD-операций с моделями SQLAlchemy.

    Использует обобщённый тип (Generic[T]) для работы с различными моделями базы данных.
    Атрибут `model` должен быть определён в подклассах и указывать на конкретную модель SQLAlchemy.
    """

    model: Type[T]

    @classmethod
    async def find_by_id(cls, model_id: int) -> Optional[T]:
        """
        Находит запись в базе данных по идентификатору.

        Args:
            model_id: Идентификатор записи.

        Returns:
            Экземпляр модели, если запись найдена, иначе None.
        """
        async with get_async_session() as session:
            result = await session.execute(select(cls.model).filter_by(id=model_id))
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by: Any) -> Optional[T]:
        """
        Находит первую запись, соответствующую переданным фильтрам.

        Args:
            **filter_by: Ключевые аргументы для фильтрации (например, column_name=value).

        Returns:
            Экземпляр модели, если запись найдена, иначе None.
        """
        async with get_async_session() as session:
            result = await session.execute(select(cls.model).filter_by(**filter_by))
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by: Any) -> List[T]:
        """
        Находит все записи, соответствующие переданным фильтрам.

        Args:
            **filter_by: Ключевые аргументы для фильтрации (например, column_name=value).

        Returns:
            Список экземпляров модели. Если записи не найдены, возвращается пустой список.
        """
        async with get_async_session() as session:
            result = await session.execute(select(cls.model).filter_by(**filter_by))
            return result.scalars().all()

    @classmethod
    async def add(cls, **data: Any) -> Optional[T]:
        """
        Создаёт новую запись в базе данных.

        Args:
            **data: Ключевые аргументы, представляющие данные для создания записи.

        Returns:
            Созданный экземпляр модели, если операция успешна, иначе None.

        Notes:
            Использует `returning` для возврата созданной записи после вставки.
        """
        async with get_async_session() as session:
            query = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one_or_none()

    @classmethod
    async def delete(cls, id: int) -> None:
        """
        Удаляет запись из базы данных по идентификатору.

        Args:
            id: Идентификатор записи для удаления.
        """
        async with get_async_session() as session:
            async with session.begin():
                await session.execute(delete(cls.model).where(cls.model.id == id))
                await session.commit()

    @classmethod
    async def update(cls, id: int, **data: Any) -> Optional[T]:
        """
        Обновляет запись в базе данных по идентификатору.

        Args:
            id: Идентификатор записи для обновления.
            **data: Ключевые аргументы, представляющие обновляемые данные.

        Returns:
            Обновлённый экземпляр модели, если запись найдена и обновлена, иначе None.
        """
        async with get_async_session() as session:
            query = update(cls.model).where(cls.model.id == id).values(**data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one_or_none()
        