from http.client import REQUEST_TIMEOUT

import frappe
from frappe import _
from frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_message.whatsapp_message import WhatsAppMessage
from frappe_whatsapp.utils import format_number
from dotenv import load_dotenv
import os
import requests
import pandas as pd
import logging
from sqlalchemy.engine import create_engine

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 10

class CustomWhatsAppMessage(WhatsAppMessage):

    def before_insert(self):
        self.set_to_from_crm_lead()
        super().before_insert()

    def before_save(self):
        self.set_to_from_crm_lead() 

    def set_to_from_crm_lead(self):
        ## Only act when a lead is selected
        if not self.get("custom_crm_lead"):
            return

        mobile_no = frappe.db.get_value("CRM Lead", self.custom_crm_lead, "mobile_no")
        frappe.msgprint(f"Fetched mobile no: {mobile_no}", alert=True, indicator="blue")
        if mobile_no:
            self.to = mobile_no
        
        else:
            frappe.throw(
                _(f"CRM Lead / Customer {self.custom_crm_lead} has no WhatsApp number"),
                title=_("Mobile number is missing")
            )


class WialonAPIError(RuntimeError):
    """ Riased when the Wialon API fails or returns an unusable response"""

class WialonConfigError(RuntimeError):
    """ Raised when required WIalon credentials or config are missing"""


def extract_from_wialon():
    load_dotenv(".env")

    BASE_URL = os.getenv("WIALON_BASE_URL")
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not BASE_URL or not api_key or not api_secret:
        raise WialonConfigError("Missing one or more required environment variables")

    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(BASE_URL, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error("Wialon API request failed", str(e))
        raise WialonAPIError("Failed to fetch data from Wialon")

    except ValueError as e:
        logger.error("Failed to parse Wialon API response as JSON objects", str(e))
        raise WialonAPIError("Invalid JSON response from Wialon")

def json_to_dataframe_object():
    wialon_response = extract_from_wialon()
    
    data_df = pd.json_normalize(wialon_response)
    logger.info("Extracted data from Wialon", len(data_df))

    if not data_df:
        return None

    return data_df    

