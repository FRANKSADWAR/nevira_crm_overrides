import frappe
from frappe.utils import get_datetime, getdate, cint
import json
from typing import Any
from frappe import _





frappe.whitelist(allow_guest = False)
def get_customer_list(search=None, page = 1, page_length=40):


    if not frappe.has_permission("Customer",ptype = "read"):
        frappe.throw(_("You do not have permission to view customers"),frappe.PermissionError())



    page = max(cint(page),1)

    page_length = min(max(cint(page_length),1), 100)


    customer_filters = {
        "disabled": 0
    }

    total_count = frappe.db.count("Customer", filters = customer_filters)

    rows = frappe.db.sql(""" 
            WITH 
                customer_list AS (
                    SELECT 
                        cu.name AS customer_id,
                        cu.customer_name, 
                        cu.payment_terms,
                        cu.mobile_no,
                        cu.email_id,
                        cu.country,
                        sp.sales_person,
                        cr.credit_limit
                    FROM `tabCustomer` AS cu
                        LEFT JOIN `tabSales Team` AS sp ON cu.name = sp.parent
                        LEFT JOIN `tabCustomer Credit Limit` AS cr ON cu.name = cr.parent
                        WHERE cu.disabled = 0
                ),
            
                customer_address AS (
                    SELECT
                        adr.name AS address_id,
                        adr.address_line1,
                        adr.city,
                        adr.pincode,
                        dnl.link_name AS customer_id,
                        dnl.link_title
                    FROM `tabAddress` AS adr 
                    INNER JOIN `tabDynamic Link` AS dnl  ON adr.name = dnl.parent
                    WHERE dnl.link_doctype = 'Customer'
                    
                ),
            
                transactions_history AS (
                    SELECT 
                        si.customer AS customer_id,
                        si.customer_name,
                        MAX(si.posting_date) AS last_transacted,
                        COUNT(si.name) AS transaction_frequency,
                        CASE
                            WHEN MAX(si.posting_date) IS NOT NULL THEN 1
                        ELSE 0 END AS transacted,
                        (SUM(si.base_grand_total)/COUNT(si.name)) AS average_cart_size,
                        SUM(si.base_grand_total) AS transaction_volume
                    FROM `tabSales Invoice` AS si 
                    WHERE 
                        si.docstatus = 1 
                        AND si.is_opening = 0
                        AND si.is_return = 0
                    GROUP BY si.customer
                    ORDER BY si.party_account_currency DESC, transaction_volume DESC
                )
                
                SELECT
                    cl.customer_id,
                    cl.customer_name,
                    IFNULL(cl.payment_terms,"NA") AS payment_terms,
                    IFNULL(cl.mobile_no,"NA") AS mobile_no,
                    IFNULL(cl.email_id,"NA") AS email_id,
                    IFNULL(cl.country,"NA") AS country,
                    IFNULL(cl.sales_person,"Not Set") AS sales_person,
                    IFNULL(cl.credit_limit,0) AS credit_limit,
                    IFNULL(ca.address_line1,"NA") AS main_address,
                    IFNULL(ca.city,"NA") AS city,
                    IFNULL(ca.pincode,"NA") AS postal_code,
                    IFNULL(th.last_transacted,"Hasn't Transacted") AS last_transacted,
                    IFNULL(th.average_cart_size,0) AS average_cart_size,
                    IFNULL(th.transaction_volume,0) AS transaction_volume 
                FROM customer_list AS cl 
                LEFT JOIN customer_address AS ca ON cl.customer_id = ca.customer_id 
                LEFT JOIN transactions_history AS th ON cl.customer_id = th.customer_id""", 
                as_dict=True)
    

    return {
        "data": rows,
        "page": page,
        "page_length": page_length,
        "total_count": total_count
    }

