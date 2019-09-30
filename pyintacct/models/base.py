from pydantic import BaseModel


class Date(BaseModel):
    year: str
    month: str
    day: str


class API21Object(BaseModel):
    """A base class for implementing API 2.1 classes."""
    @classmethod
    def create(cls) -> str:
        """The function name for creating an object of this type."""
        return f'create_{cls.__name__.lower()}'

    @classmethod
    def delete(cls) -> tuple:
        """A tuple of the function name for deleting the object
        type and the name of the XML attribute used as the key."""
        return f'delete_{cls.__name__.lower()}', 'key'
