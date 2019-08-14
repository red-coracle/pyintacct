from unittest import TestCase

from pyintacct.client import IntacctAPI
from pyintacct.models.company import Contact
from tests.config import config


class TestEndpoint(TestCase):
    def setUp(self):
        self.api = IntacctAPI(config=config)

    def tearDown(self) -> None:
        self.api.session.close()

    def test_inspect(self):
        r = self.api.inspect('CONTACT', True)
        detail = next(r.find_nodes_with_tag('Field'))
        assert 'externalDataName' in detail

    def test_inspect_name(self):
        r = self.api.inspect(detail=False, name='Sales Invoice')
        detail = next(r.find_nodes_with_tag('Field'))
        assert 'RECORDNO' in detail
