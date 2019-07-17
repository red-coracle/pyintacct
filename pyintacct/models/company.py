from pydantic import BaseModel


class Contact(BaseModel):
    contactname: str = ...
    printas: str = ...
    companyname: str = None
    taxable: bool = None