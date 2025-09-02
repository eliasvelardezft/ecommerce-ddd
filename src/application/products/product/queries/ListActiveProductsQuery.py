from pydantic import BaseModel, Field


class ListActiveProductsQuery(BaseModel):
    """Query to retrieve a list of active products."""

    category_id: str | None = Field(None, description="Optional category ID to filter by.")
