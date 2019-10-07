from pyintacct.models.company import Contact
from tests.utils import random_str


def test_contact(client, make_contact_record):
    contact_name = f'ρyIntacct-{random_str()}'
    contact = make_contact_record(contact_name)
    client.create(contact)
    contacts = client.read_by_query('CONTACT', f"CONTACTNAME = \'{contact_name}\'")
    assert len(contacts) == 1
    contact_key = contacts[0]['RECORDNO']
    client.delete('CONTACT', [contact_key])


def test_create_and_delete_api21(client, make_contact_record):
    contact_name = f'ρyIntacct-{random_str()}'
    contact = make_contact_record(contact_name)
    client.create(contact)
    client.delete(Contact, [contact.contactname])


def test_create_from_dict(client):
    name = f'MyTestContact-{random_str()}'
    contact = {'CONTACT': {'CONTACTNAME': name, 'PRINTAS': name}}
    client.create(contact)
    contact['CONTACT']['PRINTAS'] = 'MyTestContact1'
    client.update(contact)
    client.delete(Contact, [name])
