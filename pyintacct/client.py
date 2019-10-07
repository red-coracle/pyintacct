import logging
import requests
import time
from copy import deepcopy
from jxmlease import parse, XMLDictNode, XMLCDATANode
from pydantic import BaseModel
from typing import List, Type, Union
from uuid import uuid4
from .exceptions import IntacctException, IntacctServerError
from .models.base import API21Object


logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

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
    def __init__(self, config: dict = None):
        self.config = {
            'SENDER_ID': None,
            'SENDER_PW': None,
            'COMPANY_ID': None,
            'ENTITY_ID': None,
            'USER_ID': None,
            'USER_PW': None,
            'SESSION_ID': None,
            'ENDPOINT': 'https://api.intacct.com',
            'UNIQUE_ID': 'false',
            'DTD_VERSION': '3.0',
            'INCLUDE_WHITESPACE': 'true'
        }
        if config is not None:
            self.config.update(config)
        self.debug_level = logging.DEBUG
        self.session = requests.session()
        self.session.headers = {'content-type': 'application/xml',
                                'accept-encoding': '*',
                                'user-agent': 'pyintacct-0.0.7'}
        self.url = 'https://api.intacct.com/ia/xml/xmlgw.phtml'
        self.basexml = parse(BASE_XML)
        self.basexml['request']['control'].update(XMLDictNode({
            'senderid': self.config['SENDER_ID'],
            'password': self.config['SENDER_PW'],
            'controlid': uuid4(),
            'uniqueid': self.config['UNIQUE_ID'],
            'dtdversion': self.config['DTD_VERSION'],
            'includewhitespace': self.config['INCLUDE_WHITESPACE'],
        }))
        self.sessionid = None
        self.session_expiration = 0

    def execute(self, payload: XMLDictNode, refresh_session=True) -> XMLDictNode:
        """
        Sends the request to the Intacct API. Automatically refreshes session token after one hour.

        :param payload: A jxmlease structure containing the full payload except authentication.
        :param refresh_session: An override flag to allow bypassing session reuse.
        :return: A requests response.
        """
        if self.session_expiration < time.time() and refresh_session:
            try:
                self.sessionid = self.get_session_id()
                # TODO: The expiration can be obtained from the API response now.
                self.session_expiration = time.time() + 60 * 60
            except IntacctException as e:
                self.sessionid = None
                self.session_expiration = 0
        if refresh_session:
            payload['request']['operation']['authentication'].add_node(tag='sessionid',
                                                                       new_node=XMLCDATANode(self.sessionid))
        try:
            payload.standardize()
            r = self.session.post(self.url, data=payload.emit_xml().encode('utf-8'))
            if 500 <= r.status_code <= 599:
                # If a 500 error is encountered we raise IntacctServerError. The user may decide whether to retry.
                raise IntacctServerError(r.text)
            response = parse(r.text)
            if self.validate_response(response):
                return response
            else:
                raise IntacctException('Intacct API call failed.\n' + r.text)
        except requests.exceptions.RequestException as e:
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

    def get_session_id(self) -> str:
        payload = deepcopy(self.basexml)
        login = XMLDictNode({
            'userid': self.config['USER_ID'],
            'companyid': self.config['COMPANY_ID'],
            'password': self.config['USER_PW']
        })
        payload['request']['operation']['authentication'].add_node(tag='login', new_node=login)
        function = XMLDictNode(tag='function')
        function.set_xml_attr('controlid', str(uuid4()))
        function.add_node('getAPISession')
        payload['request']['operation']['content'].add_node(tag='function', new_node=function)
        response = self.execute(payload, refresh_session=False)
        sessionid = next(response.find_nodes_with_tag('sessionid'))
        return str(sessionid.text)

    def read_by_query(self, obj: str, query: str, fields: str = '*', pagesize: int = 100, docparid: str = ''):
        """TODO: support automatic deserialisation instead of returning jxmlease object
           TODO: turn into generator instead of all results at once.
        """
        payload, function = self.get_function_base()
        function.add_node(tag='readByQuery', new_node=XMLDictNode({
            'object': obj,
            'fields': fields,
            'query': query,
            'pagesize': pagesize,
            'docparid': docparid}))
        results = list()
        r = self.execute(payload)
        results.extend(r.find_nodes_with_tag(obj.lower()))
        data = next(r.find_nodes_with_tag('data'))
        remaining = data.get_xml_attr('numremaining')
        result_id = data.get_xml_attr('resultId')
        while int(remaining) > 0:
            data, remaining, result_id = self.read_more(result_id)
            results.extend(data.find_nodes_with_tag(obj.lower()))
        return results

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
            new_node = XMLDictNode(obj.dict(skip_defaults=True))
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
        if hasattr(obj, 'dict'):
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
