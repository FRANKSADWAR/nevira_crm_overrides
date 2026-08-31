from dotenv import load_dotenv, find_dotenv
import os
import frappe
from frappe.utils import get_datetime, getdate, cint
import json
from typing import Any
from frappe import _
import requests


BASEDIR = os.path.abspath((os.path.dirname(__file__)))
load_dotenv(os.path.join(BASEDIR,".env"))

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
        if deal.email != doc.emil_id or deal.mobile_no != doc.mobile_no:
            frappe.db.set_value(
                "CRM Deal",
                linked_deal.parent,
                {
                    "email": doc.email_id,
                    "mobile_no": doc.mobile_no
                }
            )

def test_get_customer_list():

    BASE_URL = "https://tst.neviraminerals.com"

    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    print(API_KEY)
    print(API_SECRET)
    headers = {
        "Authorization":f"token {API_KEY}:{API_SECRET}",
        "Content":"application/json"
    }

    params = {
        "page": 1,
        "page_length": 40
    } 

    URL = f"{BASE_URL}/api/method/neviraflow.api.get_customer_list"

    try:
        response = requests.get(URL,headers=headers, params = params)
        data = response.json()
        return data
    except Exception as e:
        print("Unbale to fetch data:",e)

    

    