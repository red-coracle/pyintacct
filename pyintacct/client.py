import logging
import time
from copy import deepcopy
from typing import List, Tuple, Union
from uuid import uuid4

import httpx
from jxmlease import parse, XMLDictNode, XMLCDATANode
from pydantic import BaseModel

from .exceptions import IntacctException, IntacctServerError
from .models.base import API21Object

logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

BASE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<request>
    <control>
        <senderid></senderid>
        <password></password>
        <controlid></controlid>
        <uniqueid></uniqueid>
        <dtdversion></dtdversion>
        <includewhitespace></includewhitespace>
    </control>
    <operation>
        <authentication></authentication>
        <content></content>
    </operation>
</request>
"""


class IntacctAPI(object):
    def __init__(self,
                 sender_id: str = None,
                 sender_password: str = None,
                 company_id: str = None,
                 entity_id: str = None,
                 user_id: str = None,
                 user_password: str = None,
                 session_id: str = None,
                 session_expiration: int = 0,
                 endpoint: str = 'https://api.intacct.com/ia/xml/xmlgw.phtml'):
        self.sender_id = sender_id
        self.sender_password = sender_password
        self.company_id = company_id
        self.entity_id = entity_id
        self.user_id = user_id
        self.user_password = user_password
        self.session_id = session_id
        self.session_expiration = session_expiration
        self.endpoint = endpoint
        self.headers = {'content-type': 'application/xml',
                        'accept-encoding': '*',
                        'user-agent': 'pyintacct-0.2.0'}
        # Auto-detect http2 is available
        http2_enabled = False
        try:
            import h2
            http2_enabled = True
        except ImportError:
            pass
        self.http_client = httpx.Client(headers=self.headers, timeout=30, http2=http2_enabled)
        self.basexml = parse(BASE_XML)
        self.basexml['request']['control'].update(XMLDictNode({
            'senderid': self.sender_id,
            'password': self.sender_password,
            'controlid': uuid4(),
            'uniqueid': 'false',
            'dtdversion': '3.0',
            'includewhitespace': 'true',
        }))

    def execute(self, payload: XMLDictNode, refresh_session=True) -> XMLDictNode:
        """
        Sends the request to the Intacct API. Automatically refreshes session token after one hour.

        :param payload: A jxmlease structure containing the full payload except authentication.
        :param refresh_session: An override flag to allow bypassing session reuse.
        :return: An XMLDictNode.
        """
        if self.session_expiration < time.time() and refresh_session:
            try:
                self.session_id, self.endpoint, timestamp = self.get_session_id()
                self.session_expiration = time.mktime(time.strptime(timestamp, '%Y-%m-%dT%H:%M:%S+00:00'))
            except IntacctException as e:
                self.session_id = None
                self.session_expiration = 0
                raise e
        if refresh_session:
            payload['request']['operation']['authentication'] \
                .add_node(tag='sessionid', new_node=XMLCDATANode(self.session_id))
        try:
            payload.standardize()
            r = self.http_client.post(self.endpoint, content=payload.emit_xml().encode('utf-8'))
            if 500 <= r.status_code <= 599:
                # If a 500 error is encountered we raise IntacctServerError. The user may decide whether to retry.
                raise IntacctServerError(r.text)
            response = parse(r.text)
            if self.validate_response(response):
                return response
            else:
                raise IntacctException('Intacct API call failed.\n' + r.text)
        except httpx.HTTPStatusError as e:
            raise IntacctException(e)

    def get_function_base(self):
        """
        Internal function to get a prepared copy of the XML request and the function node.
        :return: Tuple of the complete payload and the function node.
        """
        payload = deepcopy(self.basexml)
        content = payload['request']['operation']['content']
        function = content.add_node(tag='function', new_node=XMLDictNode(tag='function'))
        function.set_xml_attr('controlid', str(uuid4()))
        return payload, function

    @staticmethod
    def validate_response(xml: XMLDictNode) -> bool:
        """

        :param xml: jxmlease XML tree to validate.
        :return: Returns True if the tree has no error nodes,
                 otherwise raises an IntacctException with the error node contents.
        """
        msg = ''
        for node in xml.find_nodes_with_tag('error'):
            msg += f'{node.get("description")}{node.get("description2")}\n'
        if msg != '':
            raise IntacctException(msg)
        else:
            return True

    def get_session_id(self) -> Tuple[str, str, str]:
        payload = deepcopy(self.basexml)
        # Note: the login elements need to be in this order
        login = XMLDictNode({
            'userid': self.user_id,
            'companyid': self.company_id,
            'password': self.user_password
        })
        payload['request']['operation']['authentication'].add_node(tag='login', new_node=login)
        function = XMLDictNode(tag='function')
        function.set_xml_attr('controlid', str(uuid4()))
        session_node = function.add_node('getAPISession')
        if self.entity_id is not None:
            session_node.add_node('locationid', text=self.entity_id)
        payload['request']['operation']['content'].add_node(tag='function', new_node=function)
        response = self.execute(payload, refresh_session=False)
        sessionid = next(response.find_nodes_with_tag('sessionid'))
        endpoint = next(response.find_nodes_with_tag('endpoint'))
        timestamp = next(response.find_nodes_with_tag('sessiontimeout'))
        return str(sessionid.text), str(endpoint.text), str(timestamp.text)

    def read_by_query(self, obj: str, query: str, fields: str = '*', pagesize: int = 100, docparid: str = ''):
        return list(self.yield_by_query(obj, query, fields, pagesize, docparid))

    def yield_by_query(self, obj: str, query: str, fields: str = '*', pagesize: int = 100, docparid: str = ''):
        payload, function = self.get_function_base()
        function.add_node(tag='readByQuery', new_node=XMLDictNode({
            'object': obj,
            'fields': fields,
            'query': query,
            'pagesize': pagesize,
            'docparid': docparid}))
        r = self.execute(payload)
        for record in r.find_nodes_with_tag(obj.lower()):
            yield record
        data = next(r.find_nodes_with_tag('data'))
        remaining = data.get_xml_attr('numremaining')
        result_id = data.get_xml_attr('resultId')
        while int(remaining) > 0:
            data, remaining, result_id = self.read_more(result_id)
            for record in data.find_nodes_with_tag(obj.lower()):
                yield record

    def read_more(self, result_id):
        payload, function = self.get_function_base()
        function.add_node(tag='readMore', new_node=XMLDictNode({
            'resultId': result_id
        }))
        r = self.execute(payload)
        data = next(r.find_nodes_with_tag('data'))
        remaining = data.get_xml_attr('numremaining')
        result_id = data.get_xml_attr('resultId', None)
        return data, remaining, result_id

    def inspect(self, obj: str = '*', detail: bool = False, name: str = None):
        payload, function = self.get_function_base()
        inspect_node = function.add_node(tag='inspect', new_node=XMLDictNode({
            f'{"name" if name else "object"}': f'{name if name else obj}'}
        ))
        inspect_node.set_xml_attr('detail', f'{"1" if detail else "0"}')
        return self.execute(payload)

    def create(self, obj):
        payload, function = self.get_function_base()
        tag = 'create'
        if issubclass(obj.__class__, API21Object):
            tag = obj.create()
            new_node = XMLDictNode(obj.model_dump(exclude_unset=True))
        elif hasattr(obj, 'model_dump'):
            obj = dict([(obj.__class__.__name__.upper(), obj.model_dump())])
            new_node = XMLDictNode(obj)
        elif hasattr(obj, 'dict'):
            obj = dict([(obj.__class__.__name__.upper(), obj.dict())])
            new_node = XMLDictNode(obj)
        else:
            new_node = XMLDictNode(obj)
        function.add_node(tag=tag, new_node=new_node)
        return self.execute(payload)

    def update(self, obj: Union[dict, BaseModel]):
        payload, function = self.get_function_base()
        tag = 'update'
        if hasattr(obj, 'model_dump'):
            obj = dict([(obj.__class__.__name__.upper(), obj.model_dump())])
            new_node = XMLDictNode(obj)
        elif hasattr(obj, 'dict'):
            obj = dict([(obj.__class__.__name__.upper(), obj.dict())])
            new_node = XMLDictNode(obj)
        else:
            new_node = XMLDictNode(obj)
        function.add_node(tag=tag, new_node=new_node)
        return self.execute(payload)

    def _delete_v21(self, obj: type(API21Object), keys: List[str]):
        function_name, key_attr = obj.delete()
        for key in keys:
            payload, function = self.get_function_base()
            f = function.add_node(function_name)
            f.set_xml_attr(key_attr, key)
            self.execute(payload)
        return

    def delete(self, obj: Union[str, type(API21Object)], keys: List[str]):
        try:
            if issubclass(obj, API21Object):
                return self._delete_v21(obj, keys)
        except TypeError:
            pass
        payload, function = self.get_function_base()
        function.add_node(tag='delete', new_node=XMLDictNode({
            'object': obj,
            'keys': ','.join(keys)
        }))
        return self.execute(payload)
