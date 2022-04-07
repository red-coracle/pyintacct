import types

from pydantic import BaseModel

from pyintacct.client import IntacctAPI


def test_client():
    api = IntacctAPI('', '')
    assert isinstance(api, IntacctAPI)


def test_client_config():
    api = IntacctAPI('sender_id', 'sender_pass')
    assert api.sender_id == 'sender_id'
    assert api.sender_password == 'sender_pass'


def test_client_config_defaults():
    api = IntacctAPI('sender_id', 'sender_pass')
    assert api.user_id is None
    assert api.user_password is None
    assert api.session_expiration == 0
    assert api.basexml['request']['control']['senderid'] == 'sender_id'


def test_yield_by_query(client):
    class Location(BaseModel):
        LOCATIONID: str
        NAME: str
        PARENTID: str

    results = client.yield_by_query('LOCATION', query='', pagesize=3)
    assert isinstance(results, types.GeneratorType)
    for result in results:
        location = Location.parse_obj(result)
        assert location.NAME != ''
