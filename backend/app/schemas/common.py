from pydantic import BaseModel


class ErrorEnvelope(BaseModel):
    error: dict[str, str]


class Page(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
