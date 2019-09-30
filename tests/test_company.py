from unittest import TestCase

from pyintacct.client import IntacctAPI
from pyintacct.models.company import Contact, MailAddress
from tests.config import config


class TestEndpoint(TestCase):
    def setUp(self):
        self.api = IntacctAPI(config=config)
        # UTF-8 character to also test encoding.
        address = MailAddress(address1='100 Main Street',
                              address2='Suite 200',
                              city='San Francisco',
                              state='CA',
                              country='United States')
        self.contact = Contact(contactname='ρyIntacct',
                               printas='ρyIntacct 0.0.6',
                               companyname='Foobar Inc.',
                               firstname='John',
                               lastname='Smith',
                               phone1='555-555-5555',
                               mailaddress=address,
                               taxid='00-000000')

    def tearDown(self) -> None:
        self.api.session.close()

    def test_create_contact(self):
        self.api.create(self.contact)

    def test_query_and_delete_contact(self):
        contacts = self.api.read_by_query('CONTACT', 'CONTACTNAME = \'ρyIntacct\'')
        assert len(contacts) == 1
        contact_key = contacts[0]['RECORDNO']
        self.api.delete('CONTACT', [contact_key])

    def test_create_and_delete_api21(self):
        self.api.create(self.contact)
        self.api.delete(Contact, [self.contact.contactname])

    def test_create_from_dict(self):
        name = 'MyTestContact'
        contact = {'CONTACT': {'CONTACTNAME': name, 'PRINTAS': name}}
        self.api.create(contact)
        contact['CONTACT']['PRINTAS'] = 'MyTestContact1'
        self.api.update(contact)
        self.api.delete(Contact, [name])
