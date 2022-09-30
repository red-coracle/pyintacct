import pytest
from .config import config
from decimal import Decimal
from pyintacct import IntacctAPI
from pyintacct.models.base import Date
from pyintacct.models.company import Contact, MailAddress
from pyintacct.models.purchasing import POTransaction, POTransactionItem, POTransactionItems


@pytest.fixture(scope='session')
def client():
    return IntacctAPI(
        sender_id=config.SENDER_ID,
        sender_password=config.SENDER_PASSWORD,
        company_id=config.COMPANY_ID,
        user_id=config.USER_ID,
        user_password=config.USER_PASSWORD
    )


@pytest.fixture
def make_contact_record():
    def _make_contact_record(name):
        address = MailAddress(address1='100 Main Street',
                              address2='Suite 200',
                              city='San Francisco',
                              state='CA',
                              country='United States')
        contact = Contact(contactname=name,
                          printas='ρyIntacct',
                          companyname='Foobar Inc.',
                          firstname='John',
                          lastname='Smith',
                          phone1='555-555-5555',
                          mailaddress=address,
                          taxid='00-000000')
        return contact
    return _make_contact_record


@pytest.fixture
def make_podocument():
    def _make_podocument(documentno):
        potransaction = POTransaction(
            transactiontype='Purchase Order',
            datecreated=Date(year='2019', month='9', day='1'),
            vendorid='20025',
            documentno=documentno,
            referenceno=documentno,
            vendordocno='INV-00001',
            datedue=Date(year='2019', month='10', day='21'),
            returnto=Contact(contactname='EirGrid Ireland'),
            payto=Contact(contactname='EirGrid Ireland'),
            basecurr='EUR',
            currency='EUR',
            exchratetype='Intacct Daily Rate',
            potransitems=POTransactionItems(potransitem=[]))
        potransaction.potransitems.potransitem.append(POTransactionItem(
            itemid='340',
            itemdesc='Test widget #1',
            quantity=Decimal(19),
            unit='Each',
            price=Decimal('34.40'),
            locationid='500',
            departmentid='500',
            vendorid='20025'))
        potransaction.potransitems.potransitem.append(POTransactionItem(
            itemid='System Support',
            itemdesc='Support for test widget #1',
            quantity=Decimal(19),
            unit='Each',
            price=Decimal('12.40'),
            locationid='500',
            departmentid='500',
            vendorid='20025'))
        return potransaction
    return _make_podocument

