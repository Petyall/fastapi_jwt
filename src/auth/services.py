from uuid import UUID
from datetime import datetime

from sqlalchemy import update

from src.services import BaseRepository
from src.models import User, RefreshToken
from src.database import get_async_session


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для выполнения CRUD-операций с моделью User.
    """
    model = User


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Репозиторий для выполнения CRUD-операций с моделью RefreshToken.
    """
    model = RefreshToken

    @classmethod
    async def revoke(cls, jti: UUID, revoked: datetime) -> RefreshToken | None:
        """
        Отзывает refresh-токен, устанавливая дату отзыва.

        Args:
            jti: Уникальный идентификатор токена (JWT ID).
            revoked: Дата и время отзыва токена.

        Returns:
            Обновлённый экземпляр RefreshToken, если токен найден, иначе None.
        """
        async with get_async_session() as session:
            query = update(cls.model).where(cls.model.jti == jti).values(revoked=revoked).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalars().one_or_none()
        