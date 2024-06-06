import pytest
from decimal import Decimal
from pyintacct.models.base import Date
from pyintacct.models.company import Contact
from pyintacct.models.order_entry import SOTransaction, SOTransactionItem, SOTransactionItems


def test_create_sotransaction():
    items = SOTransactionItems(sotransitem=[
        SOTransactionItem(itemid='1001', quantity=Decimal('5'), unit='each', price=Decimal('100.00')),
        SOTransactionItem(itemid='1002', quantity=Decimal('3'), unit='each', price=Decimal('200.00'))
    ])

    transaction = SOTransaction(
        transactiontype='Sales Order',
        datecreated=Date(year='2024', month='6', day='18'),
        customerid='CUST-1000',
        sotransitems=items,
        termname='Net 30',
        basecurr='USD',
        currency='USD',
        exchratetype='Intacct Daily Rate'
    )

    assert transaction.transactiontype == 'Sales Order'
    assert transaction.datecreated == Date(year='2024', month='6', day='18')
    assert transaction.customerid == 'CUST-1000'
    assert transaction.sotransitems == items
    assert transaction.termname == 'Net 30'
    assert transaction.basecurr == 'USD'
    assert transaction.currency == 'USD'
    assert transaction.exchratetype == 'Intacct Daily Rate'
    assert len(transaction.sotransitems.sotransitem) == 2


def test_query_transactions(client):
    transactions = client.read_by_query('SOTRANSACTION', 'CUSTOMERID LIKE CUST%', fields='TRANSACTIONID', pagesize=3)
    assert isinstance(transactions, list)
    assert len(transactions) > 0
