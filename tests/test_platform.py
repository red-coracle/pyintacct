from unittest import TestCase

from pydantic import BaseModel
from pyintacct.client import IntacctAPI
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

    def test_create_custom_model(self):
        class Location(BaseModel):
            LOCATIONID: str
            NAME: str
            PARENTID: str

        location = Location(LOCATIONID='T123', NAME='Test Location', PARENTID='100')
        self.api.create(location)
        location.NAME = 'Testing Location'
        self.api.update(location)
        query = self.api.read_by_query('LOCATION', 'LOCATIONID = \'T123\'')
        assert len(query) == 1
        assert query[0]['NAME'] == location.NAME
        self.api.delete('LOCATION', [query[0]['RECORDNO']])
