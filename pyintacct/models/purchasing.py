from .base import API21Object, Date
from .company import Contact
from decimal import Decimal
from pydantic import BaseModel
from typing import List


class POTransactionItem(BaseModel):
    itemid: str = ...
    itemdesc: str = None
    taxable: bool = None
    warehouseid: str = None
    quantity: Decimal = ...
    unit: str = None
    linelevelsimpletaxtype: str = None
    price: Decimal = None
    sourcelinekey: int = None
    overridetaxamount: Decimal = None
    deliverto: Contact = None
    tax: Decimal = None
    locationid: str = None
    departmentid: str = None
    memo: str = None
    # itemdetails
    form1099: bool = None
    form1099type: str = None
    form1099box: str = None
    # customfields
    projectid: str = None
    customerid: str = None
    vendorid: str = None
    employeeid: str = None
    classid: str = None
    contractid: str = None
    billable: bool = None


class POTransactionItems(BaseModel):
    potransitem: List[POTransactionItem]


class POTransaction(API21Object):
    transactiontype: str = None
    datecreated: Date = None
    dateposted: Date = None
    createdfrom: str = None
    vendorid: str = None
    documentno: str = None
    referenceno: str = None
    vendordocno: str = None
    termname: str = None
    datedue: Date = None
    message: str = None
    shippingmethod: str = None
    returnto: Contact = None
    payto: Contact = None
    deliverto: Contact = None
    supdocid: str = None
    externalid: str = None
    basecurr: str = None
    currency: str = None
    exchratedate: Date = None
    exchratetype: str = None
    exchrate: Decimal = None
    # customfields
    state: str = None
    potransitems: POTransactionItems = None
    # subtotals
