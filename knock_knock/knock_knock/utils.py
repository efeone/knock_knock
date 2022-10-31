import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate
from frappe.utils import time_diff
from frappe_meta_integration.whatsapp.doctype.whatsapp_communication.whatsapp_communication import *
from frappe.utils import *

def get_access_token():
	return frappe.utils.password.get_decrypted_password(
	"WhatsApp Cloud API Settings", "WhatsApp Cloud API Settings", "access_token"
	)

@frappe.whitelist()
def get_all_dockets():
	if frappe.db.exists("Docket", {"status": "Open"}):
		dockets = frappe.db.get_all("Docket", filters = {"status": "Open"})
		if dockets:
			for docket in dockets:
				docket_doc = frappe.get_doc('Docket', docket.name)
				today = getdate(frappe.utils.today())
				mobile_no = frappe.db.get_value('User', docket_doc.owner, 'mobile_no')
				due_date = getdate(docket_doc.due_date)
				#To change status to Overdue
				if due_date>=today:
					change_docket_status(docket_doc)
				if docket_doc.remind_before_unit == 'Day':
					if docket_doc.remind_before:
						notification_date = frappe.utils.add_to_date(due_date, days=-1*docket_doc.remind_before)
					if getdate(notification_date) == today:
						create_notification_log(docket_doc.subject, docket_doc.owner, docket_doc.description, docket_doc.doctype, docket_doc.name)
						if mobile_no:
							send_whatsapp_msg(mobile_no, docket_doc.description)
				else:
					if due_date==today:
						create_notification_log(docket_doc.subject, docket_doc.owner, docket_doc.description, docket_doc.doctype, docket_doc.name)
						if mobile_no:
							send_whatsapp_msg(mobile_no, docket_doc.description)

@frappe.whitelist()
def send_whatsapp_msg(mobile_no, message_body):
	whatsapp_communication_doc = frappe.new_doc("WhatsApp Communication")
	whatsapp_communication_doc.to = mobile_no
	whatsapp_communication_doc.message_type = 'Text'
	whatsapp_communication_doc.message_body = message_body
	whatsapp_communication_doc.save()
	whatsapp_communication_doc.send_message()
	frappe.db.commit()
@frappe.whitelist()
def create_notification_log(subject, for_user, email_content, document_type, document_name):
    notification_doc = frappe.new_doc('Notification Log')
    notification_doc.subject = subject
    notification_doc.type = 'Mention'
    notification_doc.for_user = for_user
    notification_doc.email_content = email_content
    notification_doc.document_type = document_type
    notification_doc.document_name = document_name
    notification_doc.save()
    frappe.db.commit()

def change_docket_status(self):
	if self.status == 'Open':
		current_date = getdate(today())
		due_date = getdate(self.due_date)
		if current_date>due_date:
			self.status = 'Overdue'
			frappe.db.set_value(self.doctype, self.name, 'status', 'Overdue')
			frappe.db.commit()
