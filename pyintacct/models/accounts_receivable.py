import weakref
from pyintacct.models.base import Date
from decimal import Decimal
from jxmlease import XMLDictNode
from pydantic import BaseModel
from typing import List


class LineItemDetail(BaseModel):
    glaccountno: str
    amount: Decimal
    memo: str = None
    locationid: str = None
    departmentid: str = None
    customerid: str = None
    vendorid: str = None
    employeeid: str = None
    itemid: str = None
    classid: str = None
    contractid: str = None
    warehouseid: str = None


class LineItem(BaseModel):
    lineitem: List[LineItemDetail]


class ARInvoice(BaseModel):
    customerid: str = ...
    datecreated: Date = ...
    dateposted: Date = None
    datedue: Date = None
    termname: str = None
    action: str = ...
    invoiceno: str = None
    ponumber: str = None
    description: str = None
    basecurr: str = None
    currency: str = None
    exchratetype: str = None
    invoiceitems: LineItem = ...
