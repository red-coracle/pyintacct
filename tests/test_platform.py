from pydantic import BaseModel

from .utils import random_str


def test_inspect(client):
    r = client.inspect('CONTACT', True)
    detail = next(r.find_nodes_with_tag('Field'))
    assert 'externalDataName' in detail


def test_inspect_name(client):
    r = client.inspect(detail=False, name='Sales Invoice')
    detail = next(r.find_nodes_with_tag('Field'))
    assert 'RECORDNO' in detail


def test_create_custom_model(client):
    class Location(BaseModel):
        LOCATIONID: str
        NAME: str
        PARENTID: str

    location = Location(LOCATIONID=random_str(5), NAME='Test Location', PARENTID='100')
    client.create(location)
    location.NAME = 'Testing Location'
    client.update(location)
    query = client.read_by_query('LOCATION', f'LOCATIONID = \'{location.LOCATIONID}\'')
    assert len(query) == 1
    assert query[0]['NAME'] == location.NAME
    client.delete('LOCATION', [query[0]['RECORDNO']])


def test_parse_models(client):
    class Location(BaseModel):
        LOCATIONID: str
        NAME: str
        PARENTID: str

    results = client.read_by_query('LOCATION', query='')
    for result in results:
        location = Location.parse_obj(result)
        assert location.NAME != ''
