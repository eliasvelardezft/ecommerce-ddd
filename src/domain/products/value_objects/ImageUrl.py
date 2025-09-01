from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ImageUrl(BaseModel):
    """Represents a URL for a product image, with optional alt text."""
    url: HttpUrl = Field(..., description="The full URL of the image.")
    alt_text: Optional[str] = Field(None, description="Alternative text for the image, for accessibility.")
