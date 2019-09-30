from .base import API21Object
from pydantic import BaseModel
from typing import Optional


class MailAddress(BaseModel):
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    isocountrycode: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class Contact(API21Object):
    contactname: str = ...
    printas: Optional[str] = None
    companyname: Optional[str] = None
    taxable: Optional[bool] = None
    taxgroup: Optional[str] = None
    prefix: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    initial: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    cellphone: Optional[str] = None
    pager: Optional[str] = None
    fax: Optional[str] = None
    email1: Optional[str] = None
    email2: Optional[str] = None
    url1: Optional[str] = None
    url2: Optional[str] = None
    status: Optional[str] = None
    mailaddress: Optional[MailAddress] = None
    taxid: Optional[str] = None

    @classmethod
    def delete(cls):
        return 'delete_contact', 'contactname'
