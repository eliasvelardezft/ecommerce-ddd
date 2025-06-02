from pydantic import BaseModel, Field, AnyHttpUrl


class ImageUrl(BaseModel):
    url: AnyHttpUrl
    alt_text: str = Field(min_length=1, max_length=255)
