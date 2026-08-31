import frappe
from frappe.utils import get_datetime, getdate, cint
import json
from typing import Any
from frappe import _

def test_valid(doc, method = None):
    pass

def update_deals_email_mobile(doc):
    linked_deals = frappe.get_all(
        "CRM Contacts",
        filters = {"contact":doc.name, "is_primary":1},
        fields =["parent"]
    )

    for linked_deal in linked_deals:
        deal = frappe.db.get_values("CRM Deal", linked_deal.parent, ["email","mobile_no"], as_dict=True)