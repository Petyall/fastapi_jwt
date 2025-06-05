from uuid import UUID
from datetime import datetime

from sqlalchemy import update

from src.services import BaseRequests
from src.models import RefreshToken, User
from src.database import async_session_maker


class UserRequests(BaseRequests):
    model = User


class RefreshTokenService(BaseRequests):

    model = RefreshToken

    @classmethod
    async def revoke(cls, jti: UUID, revoked: datetime):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.jti == jti).values(revoked=revoked).returning(cls.model)
            result = await session.execute(query)
            await session.commit()

            updated_object = result.scalars().one_or_none()
            return updated_object
