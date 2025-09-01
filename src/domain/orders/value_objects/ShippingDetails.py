from typing import Annotated, Optional

from pydantic import BaseModel, Field, field_validator


class ShippingDetails(BaseModel):
    address_line1: Annotated[str, Field(min_length=1, max_length=255)]
    address_line2: Annotated[str, Field(max_length=255)] | None = None # Optional can wrap Annotated
    city: Annotated[str, Field(min_length=1, max_length=100)]
    state_province: Annotated[str, Field(min_length=1, max_length=100)]
    postal_code: Annotated[str, Field(min_length=1, max_length=20)]
    country: Annotated[str, Field(min_length=1, max_length=50)]
    phone_number: Annotated[str, Field(min_length=1, max_length=20)]

    model_config = {
        "frozen": True,
        "extra": "forbid"
    }

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        cleaned = value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if not cleaned.isdigit():
            raise ValueError("Phone number must contain only digits and optional '+', '-', ' ', '(', ')' characters")
        return value

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, value: str) -> str:
        cleaned = value.replace(" ", "").replace("-", "") # Allow hyphens in postal codes before checking isalnum
        if not cleaned.isalnum():
            raise ValueError("Postal code must contain only alphanumeric characters, spaces, and hyphens (hyphens are removed for validation check but allowed in original).")
        return value
