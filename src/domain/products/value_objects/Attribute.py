from pydantic import BaseModel, Field


class Attribute(BaseModel):
    """Represents a product attribute as a simple name-value pair."""
    name: str = Field(..., min_length=1, description="Name of the attribute (e.g., 'Color', 'Size')")
    value: str = Field(..., min_length=1, description="Value of the attribute (e.g., 'Red', 'XL')")
