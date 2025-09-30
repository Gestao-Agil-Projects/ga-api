from abc import ABC
from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import ClauseElement, delete, exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ga_api.db.dependencies import get_db_session

T = TypeVar("T")


class AbstractDAO(Generic[T], ABC):
    """
    Abstract DAO for generic CRUD operations on any model.
    """

    def __init__(
        self,
        model: Type[T],
        session: AsyncSession = Depends(get_db_session),
    ) -> None:
        self.__model = model
        self._session = session

    async def save(self, obj: T) -> T:
        """
        Saves an object to the database.
        Raises HTTP 400 if it already exists (IntegrityError).
        """
        self._session.add(obj)

        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise HTTPException(status_code=400, detail="Object already exists") from e

        return obj

    async def save_all(self, obj_list: List[T]) -> List[T]:
        """
        Saves an object list to the database.
        Raises HTTP 400 if it already exists (IntegrityError).
        """
        self._session.add_all(obj_list)

        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise HTTPException(status_code=400, detail="Object already exists") from e

        return obj_list

    async def find_by_id(self, obj_id: UUID | int) -> Optional[T]:
        """
        Finds an object by its ID.
        Returns None if not found.
        """
        result = await self._session.execute(
            select(self.__model).where(self.__model.id == obj_id),  # type: ignore
        )
        return result.scalar_one_or_none()

    async def find_all(self, limit: int = 50, offset: int = 0) -> List[T]:
        """
        Returns a list of objects with pagination (limit/offset).
        """
        result = await self._session.execute(
            select(self.__model).offset(offset).limit(limit),
        )
        return result.scalars().all()  # type: ignore

    async def delete(self, obj: T) -> None:
        """
        Deletes the provided object from the database.
        """
        await self._session.delete(obj)
        await self._session.flush()

    async def delete_by_id(self, obj_id: UUID | int) -> None:
        """
        Deletes an object by its ID.
        Does not raise an error if the object does not exist.
        """
        await self._session.execute(
            delete(self.__model).where(self.__model.id == obj_id),  # type: ignore
        )
        await self._session.flush()

    async def update(self, obj: T, data: dict[str, Any]) -> T:
        """
        Updates the fields of an existing object.
        Raises HTTP 400 if a database constraint is violated.
        """
        for field, value in data.items():
            setattr(obj, field, value)

        self._session.add(obj)

        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Update would violate a database constraint",
            ) from e

        return obj

    async def exists(self, *conditions: ClauseElement, **filters: Any) -> bool:
        """
        Checks if at least one record exists that satisfies the filters.
        - filters: dictionary for equality checks {field=value}
        - conditions: additional SQLAlchemy expressions (comparisons, ranges, etc.)
        """
        if not filters and not conditions:
            return False

        where_clauses = [
            getattr(self.__model, field) == value for field, value in filters.items()
        ]

        stmt = select(exists().where(*where_clauses, *conditions))  # type: ignore
        result = await self._session.execute(stmt)
        return bool(result.scalar())
