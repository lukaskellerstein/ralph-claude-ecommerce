import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


@dataclass
class CurrentUser:
    """Represents the currently authenticated user."""

    id: uuid.UUID
    email: str
    name: str


async def get_current_user_optional(request: Request) -> CurrentUser | None:
    """Extract current user from request if authenticated.

    Returns None if no valid authentication is present.
    This is a placeholder — will be replaced when auth feature is implemented.
    """
    # Placeholder: check for a user-id header (for development/testing)
    user_id = request.headers.get("x-user-id")
    user_email = request.headers.get("x-user-email")
    user_name = request.headers.get("x-user-name")

    if user_id and user_email and user_name:
        try:
            return CurrentUser(
                id=uuid.UUID(user_id),
                email=user_email,
                name=user_name,
            )
        except ValueError:
            return None
    return None


async def get_current_user(
    user: CurrentUser | None = Depends(get_current_user_optional),
) -> CurrentUser:
    """Require an authenticated user. Raises 401 if not authenticated."""
    if user is None:
        from app.core.errors import UnauthorizedError

        raise UnauthorizedError()
    return user
