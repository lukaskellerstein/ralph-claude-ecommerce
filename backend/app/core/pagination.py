import base64
import json
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, asc, desc, tuple_

from app.core.errors import InvalidCursorError


@dataclass
class CursorPage:
    """Result of a cursor-paginated query."""

    items: list[Any]
    next_cursor: str | None
    has_next_page: bool


def encode_cursor(sort_value: Any, record_id: uuid.UUID) -> str:
    """Encode sort value and ID into an opaque base64 cursor token."""
    payload = json.dumps({"s": str(sort_value), "id": str(record_id)})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: str) -> tuple[str, uuid.UUID]:
    """Decode an opaque cursor token into (sort_value, id).

    Raises InvalidCursorError if cursor is malformed.
    """
    try:
        payload = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        sort_value = payload["s"]
        record_id = uuid.UUID(payload["id"])
    except (json.JSONDecodeError, KeyError, ValueError, UnicodeDecodeError) as e:
        raise InvalidCursorError() from e
    return sort_value, record_id


def apply_cursor_pagination(
    query: Select[Any],
    sort_column: Any,
    id_column: Any,
    page_size: int,
    after: str | None = None,
    sort_direction: str = "desc",
) -> Select[Any]:
    """Apply cursor-based pagination to a SQLAlchemy Select query.

    Args:
        query: Base SQLAlchemy Select query
        sort_column: Column to sort by
        id_column: UUID primary key column
        page_size: Number of items per page
        after: Opaque cursor token (or None for first page)
        sort_direction: "asc" or "desc"

    Returns:
        Modified query with cursor WHERE clause, ORDER BY, and LIMIT applied.
    """
    order_fn = asc if sort_direction == "asc" else desc

    if after:
        sort_value, cursor_id = decode_cursor(after)
        # For descending: WHERE (sort_col, id) < (:sort_value, :cursor_id)
        # For ascending:  WHERE (sort_col, id) > (:sort_value, :cursor_id)
        if sort_direction == "asc":
            query = query.where(
                tuple_(sort_column, id_column) > tuple_(sort_value, cursor_id)
            )
        else:
            query = query.where(
                tuple_(sort_column, id_column) < tuple_(sort_value, cursor_id)
            )

    query = query.order_by(order_fn(sort_column), order_fn(id_column))
    # Fetch one extra to determine has_next_page
    query = query.limit(page_size + 1)

    return query


def build_cursor_page(
    rows: list[Any],
    page_size: int,
    sort_column_name: str,
) -> CursorPage:
    """Build a CursorPage from query results.

    Args:
        rows: List of SQLAlchemy model instances (may have page_size + 1 items)
        page_size: Requested page size
        sort_column_name: Name of the sort column attribute on the model

    Returns:
        CursorPage with items, next_cursor, and has_next_page
    """
    has_next_page = len(rows) > page_size
    items = rows[:page_size]

    next_cursor = None
    if has_next_page and items:
        last_item = items[-1]
        sort_value = getattr(last_item, sort_column_name)
        next_cursor = encode_cursor(sort_value, last_item.id)

    return CursorPage(
        items=items,
        next_cursor=next_cursor,
        has_next_page=has_next_page,
    )
