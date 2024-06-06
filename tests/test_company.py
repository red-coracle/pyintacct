import pytest
from decimal import Decimal
from pyintacct.models.company import Contact, MailAddress, SupDoc, Attachment, AttachmentDetail
from pyintacct.models.base import Date
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


def test_create_contact_with_mailaddress(client):
    contact_name = f'ρyIntacct-{random_str()}'
    mail_address = MailAddress(
        address1='123 Main St',
        city='Anytown',
        state='CA',
        zip='12345',
        country='USA'
    )
    contact = Contact(
        contactname=contact_name,
        mailaddress=mail_address
    )
    client.create(contact)
    contacts = client.read_by_query('CONTACT', f"CONTACTNAME = \'{contact_name}\'")
    assert len(contacts) == 1
    contact_key = contacts[0]['RECORDNO']
    client.delete('CONTACT', [contact_key])


def test_create_contact_with_supdoc(client):
    contact_name = f'ρyIntacct-{random_str()}'
    attachment_detail = AttachmentDetail(
        attachmentname='test_attachment',
        attachmenttype='PDF',
        attachmentdata='base64encodedstring'
    )
    attachment = Attachment(attachment=[attachment_detail])
    supdoc = SupDoc(
        supdocid='SUPDOC-001',
        supdocdescription='Test SupDoc',
        attachments=attachment
    )
    contact = Contact(
        contactname=contact_name,
        printas=contact_name,
        supdoc=supdoc
    )
    client.create(contact)
    contacts = client.read_by_query('CONTACT', f"CONTACTNAME = \'{contact_name}\'")
    assert len(contacts) == 1
    contact_key = contacts[0]['RECORDNO']
    client.delete('CONTACT', [contact_key])


def test_create_contact_with_full_details(client):
    contact_name = f'ρyIntacct-{random_str()}'
    mail_address = MailAddress(
        address1='123 Main St',
        city='Anytown',
        state='CA',
        zip='12345',
        country='USA'
    )
    attachment_detail = AttachmentDetail(
        attachmentname='test_attachment',
        attachmenttype='PDF',
        attachmentdata='base64encodedstring'
    )
    attachment = Attachment(attachment=[attachment_detail])
    supdoc = SupDoc(
        supdocid='SUPDOC-001',
        supdocdescription='Test SupDoc',
        attachments=attachment
    )
    contact = Contact(
        contactname=contact_name,
        printas=contact_name,
        companyname='MyCompany',
        phone1='123-456-7890',
        email1='test@example.com',
        mailaddress=mail_address,
        supdoc=supdoc
    )
    client.create(contact)
    contacts = client.read_by_query('CONTACT', f"CONTACTNAME = \'{contact_name}\'")
    assert len(contacts) == 1
    contact_key = contacts[0]['RECORDNO']
    client.delete('CONTACT', [contact_key])


@pytest.fixture
def make_contact_record():
    def _make_contact(contact_name):
        return Contact(
            contactname=contact_name,
            printas=contact_name
        )
    return _make_contact
