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
    load_dotenv(".env")

    BASE_URL = "https://tst.neviraminerals.com/"

    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        frappe.log_error(
            title="Missing API credentials",
            message ="API Key or API Secret not found in config file"
        )
        raise ValueError("API credentials not found!")
    
    headers = {
        "Authorization":f"token {api_key}:{api_secret}",
        "Content-Type":"application/json",
        "Accept":"application/json"
    }

    params = {
        "page": 1,
        "page_length": 40
    } 

    URL = f"{BASE_URL}api/method/neviraflow.api.get_customer_list"
    print(URL)

    try:
        response = requests.get(URL,headers=headers, params = params)
        response.raise_for_status()

        # Parse JSON  response
        data = response.json()

        # log success fetching of data
        frappe.logger().info(f"Successfully fetched customer data count={len(data["message"])}")
        return data
    except requests.exceptions.Timeout:
        error_message = "Request timeout"
        frappe.log_error(title="API Timeout Error", message=error_message)
        raise requests.exceptions.RequestException(error_message)

    except requests.exceptions.RequestException as e:
        error_message = f"Request failed: str(e)"
        frappe.log_error(title="API Request failed", message=error_message)
        raise
    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP error occured:{e.response.status_code} - {e.response.text}"
        frappe.log_error(title="API HTTP Error", message=error_message)
        raise


    

if __name__ == "__main__":
    data = test_get_customer_list()
    print(data)
