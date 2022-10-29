# Copyright (c) 2022, efeone Software Lab and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Docket(Document):
	pass

@frappe.whitelist()
def add_docket_comment(reason, name):
	if frappe.db.exists('Docket', name):
		doc_name= frappe.get_doc('Docket', name)
		doc_name.add_comment('Comment', reason)
		doc_name.save()
		return True
