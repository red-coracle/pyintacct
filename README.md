## pyintacct ##
[![PyPI](https://img.shields.io/pypi/dm/pyintacct.svg?style=flat-square)](https://pypi.org/project/pyintacct)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A simple Python SDK for Sage Intacct.


**Requirements**
  - Python >= 3.6
  - pydantic
  - requests
  - jxmlease


**Links**
  - [Issues](https://github.com/red-coracle/pyintacct/issues)
  - [Pull requests](https://github.com/red-coracle/pyintacct/pulls)
  - [Releases](https://github.com/red-coracle/pyintacct/releases)
  - [PyPI](https://pypi.org/project/pyintacct)
  - [License](https://github.com/red-coracle/pyintacct/blob/master/LICENSE)

**Installation**
  
  `pip install pyintacct`

**Example usage**
```python
from pyintacct import IntacctAPI

config = {'SENDER_ID': 'senderid',
          'SENDER_PW': 'senderpassword',
          'COMPANY_ID': 'mycompany',
          'USER_ID': 'username',
          'USER_PW': 'password'}
client = IntacctAPI(config)

customer = {'customer': {'CUSTOMERID': 'C-0001', 'NAME': 'Acme, Inc.'}}
client.create(customer)

r = client.read_by_query('CUSTOMER', 'CUSTOMERID = \'C-0001\'', fields='NAME', pagesize=1)
```

You can also use pydantic models:
```python
from pydantic import BaseModel

# API 3.0
class Location(BaseModel):
    LOCATIONID: str
    NAME: str

location = Location(LOCATIONID='T123', NAME='Test Location', PARENTID='100')
client.create(location)


# API 2.1
from pyintacct.models.base import API21Object

class Contact(API21Object):
    contactname: str = ...
    printas: str = None  # Need to assign a default to preserve ordering

    # Override create or delete method to fit your object.
    @classmethod
    def delete(cls):
        return 'delete_contact', 'contactname'
```
