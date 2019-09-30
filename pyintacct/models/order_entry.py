from .base import API21Object, Date
from .company import Contact
from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional


class SOTransactionItem(BaseModel):
    bundlenumber: Optional[str] = None
    itemid: str = ...
    itemdesc: Optional[str] = None
    taxable: Optional[bool] = None
    warehouseid: Optional[str] = None
    quantity: Decimal = ...
    unit: str = ...
    linelevelsimpletax: Optional[str] = None
    discountpercent: Optional[Decimal] = None
    price: Decimal = ...
    sourcelinekey: Optional[int] = None
    discsurchargememo: Optional[str] = None
    locationid: Optional[str] = None
    departmentid: Optional[str] = None
    memo: Optional[str] = None
    # itemdetails
    # customfields
    revrectemplate: Optional[str] = None
    revrecstartdate: Optional[Date] = None
    revrecenddate: Optional[Date] = None
    renewalmacro: Optional[str] = None
    projectid: Optional[str] = None
    customerid: Optional[str] = None
    vendorid: Optional[str] = None
    employeeid: Optional[str] = None
    classid: Optional[str] = None
    contractid: Optional[str] = None
    # fulfillmentstatus
    taskno: Optional[str] = None
    billingtemplate: Optional[str] = None
    dropship: Optional[bool] = None
    shipto: Optional[Contact] = None


class SOTransactionItems(BaseModel):
    sotransitem: List[SOTransactionItem]


class SOTransaction(API21Object):
    transactiontype: str = ...
    datecreated: Date = ...
    dateposted: Optional[Date] = None
    createdfrom: Optional[str] = None
    customerid: str = ...
    documentno: Optional[str] = None
    origdocdate: Optional[Date] = None
    referenceno: Optional[str] = None
    termname: Optional[str] = None
    datedue: Optional[Date] = None
    message: Optional[str] = None
    shippingmethod: Optional[str] = None
    shipto: Optional[Contact] = None
    billto: Optional[Contact] = None
    supdocid: Optional[str] = None
    externalid: Optional[str] = None
    basecurr: Optional[str] = None
    currency: Optional[str] = None
    exchratedate: Optional[Date] = None
    exchratetype: Optional[str] = None
    exchrate: Optional[str] = None
    vsoepricelist: Optional[str] = None
    # customfields
    state: Optional[str] = None
    projectid: Optional[str] = None
    sotransitems: SOTransactionItems = ...
    # subtotals
