from unittest import TestCase

from pyintacct.client import IntacctAPI
from pyintacct.models.company import Contact
from tests.config import config


class TestEndpoint(TestCase):
    def setUp(self):
        self.api = IntacctAPI(config=config)

    def tearDown(self) -> None:
        self.api.session.close()

    def test_create_contact(self):
        contact = Contact(contactname='PyIntacct', printas='PyIntacct 0.0.3')
        self.api.create(contact)

    def test_query_and_delete_contact(self):
        contacts = self.api.read_by_query('CONTACT', 'CONTACTNAME = \'PyIntacct\'')
        assert len(contacts) == 1
        self.contact_key = contacts[0]['RECORDNO']
        self.api.delete('CONTACT', [self.contact_key])
