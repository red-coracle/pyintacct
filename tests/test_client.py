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
