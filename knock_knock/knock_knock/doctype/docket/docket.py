# Copyright (c) 2022, efeone Software Lab and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import *
from frappe.model.document import Document
from knock_knock.knock_knock.utils import change_docket_status
from frappe import _

class Docket(Document):
	def validate(self):
		change_docket_status(self)
		change_due_status(self)

@frappe.whitelist()
def add_docket_comment(name, new_date, reason=None):
	if frappe.db.exists('Docket', name):
		doc_name = frappe.get_doc('Docket', name)
		doc_name.due_date = new_date
		doc_name.status = "Open"
		if reason:
			doc_name.add_comment('Comment', reason)
		doc_name.save()
		return True

def change_due_status(self):
	if str(self.due_date) < str(self.posting_date):
		frappe.throw(title = _('ALERT !!'),
			msg = _('Cannot select Past date in To date !')
		)
