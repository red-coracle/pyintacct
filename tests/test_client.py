from pyintacct.client import IntacctAPI
from unittest import TestCase


class TestClient(TestCase):
    def test_client(self):
        api = IntacctAPI()
        self.assertIsInstance(api, IntacctAPI)

    def test_client_config(self):
        api = IntacctAPI()
        self.assertTrue(all(item in api.config.items() for item in {'SENDER_ID': None, 'SENDER_PW': None}.items()))

    def test_client_config_defaults(self):
        config = {'SENDER_ID': 'mysender', 'SENDER_PW': 'mysenderpw'}
        api = IntacctAPI(config=config)
        self.assertTrue(all(item in api.config.items() for item in {'SENDER_ID': 'mysender', 'SENDER_PW': 'mysenderpw'}.items()))
        self.assertTrue(all(item in api.config.items() for item in {'USER_ID': None, 'USER_PW': None}.items()))
        self.assertTrue(api.basexml['request']['control']['senderid'] == 'mysender')
