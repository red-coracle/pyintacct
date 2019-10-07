from pyintacct.models.purchasing import POTransaction, POTransactionItems, POTransactionItem
from tests.utils import random_str


def test_potransaction(client, make_podocument):
    reference_number = f'INV-{random_str()}'
    potransaction = make_podocument(reference_number)
    client.create(potransaction)
    query = f'PONUMBER = \'{reference_number}\''
    podocument = client.read_by_query('PODOCUMENT', query, fields='DOCID', pagesize=3, docparid='Purchase Order')
    assert len(podocument) == 1
    docid = podocument[0]['DOCID']
    client.delete(POTransaction, [docid])
