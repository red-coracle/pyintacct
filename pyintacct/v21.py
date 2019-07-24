import weakref
from .models.accounts_receivable import ARInvoice
from .models.company import Contact
from .models.order_entry import SOTransaction
from jxmlease import XMLDictNode


class API21(object):
    """Container for v2.1 object-specific methods.
       TODO: Combine into a generic option based on model class?
        We try to avoid these anyway.
    """
    def __init__(self, parent):
        self.parent = weakref.ref(parent)

    def create_contact(self, contact: Contact):
        payload, function = self.parent().get_function_base()
        function.add_node('create_contact', new_node=XMLDictNode(contact.dict(skip_defaults=True)))
        return self.parent().execute(payload)

    def create_invoice(self, invoice: ARInvoice) -> XMLDictNode:
        payload, function = self.parent().get_function_base()
        function.add_node('create_invoice', new_node=XMLDictNode(invoice.dict(skip_defaults=True)))
        return self.parent().execute(payload)

    def create_sotransaction(self, sotransaction: SOTransaction) -> XMLDictNode:
        payload, function = self.parent().get_function_base()
        function.add_node('create_sotransaction', new_node=XMLDictNode(sotransaction.dict(skip_defaults=True)))
        return self.parent().execute(payload)
