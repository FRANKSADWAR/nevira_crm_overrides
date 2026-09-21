import frappe
from frappe import _
from frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_message.whatsapp_message import WhatsAppMessage
from frappe_whatsapp.utils import format_number



class CustomWhatsAppMessage(WhatsAppMessage):

    def __str__(self):
        return super().__str__()

    def before_save(self):
        self.set_to_from_crm_lead() 

    def set_to_from_crm_lead(self):

        ## Only act when a lead is selected
        if not self.get("custom_crm_lead"):
            return

        mobile_no = frappe.db.get_value("CRM Lead", self.custom_crm_lead, "mobile_no")
        if mobile_no:
            self.to = format_number(mobile_no)
        
        else:
            frappe.throw(
                _(f"CRM Lead / Customer {self.custom_crm_lead} has no WhatsApp number"),
                title=_("Mobile number is missing")
            )
