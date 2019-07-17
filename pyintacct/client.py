import logging
import requests
import time
from copy import deepcopy
from jxmlease import parse, XMLDictNode, XMLCDATANode
from pydantic import BaseModel
from typing import List
from uuid import uuid4
from .exceptions import IntacctException, IntacctServerError
from .v21 import API21


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
            'INCLUDE_WHITEPSPACE': 'true'
        }
        if config is not None:
            self.config.update(config)
        self.debug_level = logging.DEBUG
        self.session = requests.session()
        self.session.headers = {'content-type': 'application/xml',
                                'accept-encoding': '*',
                                'user-agent': 'pyintacct-0.0.3'}
        self.url = 'https://api.intacct.com/ia/xml/xmlgw.phtml'
        self.basexml = parse(BASE_XML)
        self.basexml['request']['control'].update(XMLDictNode({
            'senderid': self.config['SENDER_ID'],
            'password': self.config['SENDER_PW'],
            'controlid': uuid4(),
            'uniqueid': self.config['UNIQUE_ID'],
            'dtdversion': self.config['DTD_VERSION'],
            'includewhitespace': self.config['INCLUDE_WHITEPSPACE'],
        }))
        self.sessionid = None
        self.session_expiration = 0
        self.v21 = API21(parent=self)  # For using 2.1 specific methods.

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
            r = self.session.post(self.url, data=payload.emit_xml())
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

    def read_by_query(self, obj: str, query: str, fields: str = '*', pagesize: int = 100):
        """TODO: support automatic deserialisation instead of returning jxmlease object"""
        payload, function = self.get_function_base()
        function.add_node(tag='readByQuery', new_node=XMLDictNode({
            'object': obj,
            'fields': fields,
            'query': query,
            'pagesize': pagesize}))
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

    def create(self, obj):
        if issubclass(obj.__class__, BaseModel):
            obj = dict([(obj.__class__.__name__.upper(), obj.dict())])
        payload, function = self.get_function_base()
        function.add_node(tag='create', new_node=XMLDictNode(obj))
        return self.execute(payload)

    def update(self, obj: dict):
        payload, function = self.get_function_base()
        function.add_node(tag='update', new_node=XMLDictNode(obj))
        return self.execute(payload)

    def delete(self, obj: str, keys: List[str]):
        payload, function = self.get_function_base()
        function.add_node(tag='delete', new_node=XMLDictNode({
            'object': obj,
            'keys': ','.join(keys)
        }))
        return self.execute(payload)
