from decimal import Decimal

from pyintacct.models.accounts_receivable import ARInvoice, LineItem, LineItemDetail
from pyintacct.models.base import Date


def test_create_arinvoice(client):
    items = LineItem(lineitem=[LineItemDetail(glaccountno='4100', amount=Decimal('900.01'), customerid='10001',
                                              locationid='100'),
                               LineItemDetail(glaccountno='4120', amount=Decimal('80.011'), customerid='10001',
                                              locationid='100')])
    invoice = ARInvoice(customerid='10001',
                        datecreated=Date(year='2019', month='7', day='16'),
                        termname='Net 30',
                        action='Submit',
                        invoiceno='INV-1000',
                        basecurr='USD',
                        currency='USD',
                        exchratetype='Intacct Daily Rate',
                        invoiceitems=items)
    # client.v21.create_invoice(invoice)


def test_query_customers(client):
    customers = client.read_by_query('CUSTOMER', 'CUSTOMERID LIKE 1000%', fields='CUSTOMERID', pagesize=3)
    assert isinstance(customers, list)
    assert len(customers) == 9
