from decimal import Decimal
from unittest import TestCase

from pyintacct.client import IntacctAPI
from pyintacct.models.base import Date
from pyintacct.models.company import Contact
from pyintacct.models.purchasing import POTransaction, POTransactionItems, POTransactionItem
from tests.config import config


class TestEndpoint(TestCase):
    def setUp(self):
        self.api = IntacctAPI(config=config)

    def tearDown(self) -> None:
        self.api.session.close()

    def test_create_potransaction(self):
        potransaction = POTransaction(
            transactiontype='Purchase Order',
            datecreated=Date(year='2019', month='9', day='1'),
            vendorid='20025',
            referenceno='EirGrid Invoice INV-00001',
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
            vendorid='20025'
        ))
        potransaction.potransitems.potransitem.append(POTransactionItem(
            itemid='System Support',
            itemdesc='Support for test widget #1',
            quantity=Decimal(19),
            unit='Each',
            price=Decimal('12.40'),
            locationid='500',
            departmentid='500',
            vendorid='20025'
        ))
        self.api.create(potransaction)

    def test_query_and_delete_podocument(self):
        query = 'PONUMBER = \'EirGrid Invoice INV-00001\''
        podocument = self.api.read_by_query('PODOCUMENT', query, fields='DOCID', pagesize=3, docparid='Purchase Order')
        assert len(podocument) == 1
        docid = podocument[0]['DOCID']
        self.api.delete(POTransaction, [docid])
