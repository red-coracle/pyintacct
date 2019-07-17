from pydantic import BaseModel


class Date(BaseModel):
    year: str
    month: str
    day: str
