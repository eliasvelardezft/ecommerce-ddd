from pydantic import BaseModel, Field


class Attribute(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    value: str = Field(min_length=1, max_length=255)
