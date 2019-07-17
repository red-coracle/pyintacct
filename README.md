## pyintacct ##

A simple Python SDK for Sage Intacct.


**Requirements**
  - Python >= 3.6
  - requests
  - jxmlease


**Links**
  - [Issues](https://github.com/red-coracle/pyintacct/issues)
  - [Pull requests](https://github.com/red-coracle/pyintacct/pulls)
  - [Releases](https://github.com/red-coracle/pyintacct/releases)
  - [PyPI](https://pypi.org/project/pyintacct)
  - [License]()

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

You can also use pydantic models. See `pyintacct.models` for examples.
