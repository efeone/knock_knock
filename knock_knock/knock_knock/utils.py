import frappe
from frappe.model.document import Document
from frappe_meta_integration.whatsapp.doctype.whatsapp_communication.whatsapp_communication import *
from frappe.utils import *
import re
from frappe.utils.user import get_users_with_role

def get_access_token():
	return frappe.utils.password.get_decrypted_password(
		"WhatsApp Cloud API Settings", "WhatsApp Cloud API Settings", "access_token"
	)

@frappe.whitelist()
def daily_docket_scheduler():
	current_date = getdate(today())
	dockets = frappe.db.get_all('Docket', filters = { 'status': 'Open', 'remind_before_unit': 'Day'})
	if dockets:
		for docket in dockets:
			docket_doc = frappe.get_doc('Docket', docket.name)
			mobile_no = frappe.db.get_value('User', docket_doc.owner, 'mobile_no')
			due_date = getdate(docket_doc.due_date)
			docket_url = get_url_to_form(docket_doc.doctype, docket_doc.name)
			docket_due_message_mail = 'Docket '+ docket_doc.name + ' for '+ docket_doc.subject + ' had Overdue on '+ str(docket_doc.due_date)
			docket_due_message_wtsp = 'Docket '+ docket_doc.name + ' for '+ docket_doc.subject + ' had Overdue on *'+ str(docket_doc.due_date) + '*.\nReference : ' + docket_url

			# Changing Status to Overdue and notifications
			if due_date<current_date:
				change_docket_status(docket_doc)
				create_notification_log(docket_doc.subject+ 'is Overdue', docket_doc.owner, docket_due_message_mail, docket_doc.doctype, docket_doc.name)
				if mobile_no:
					send_whatsapp_msg(mobile_no, docket_due_message_wtsp, docket_doc.doctype, docket_doc.name)

			#Daily Scheduler Checking and notifications
			if docket_doc.remind_before_unit == 'Day':
				if docket_doc.remind_before:
					notification_date = frappe.utils.add_to_date(due_date, days=-1*docket_doc.remind_before)
				else:
					notification_date = due_date
			if getdate(notification_date) == current_date:
				create_notification_log(docket_doc.subject, docket_doc.owner, docket_doc.description, docket_doc.doctype, docket_doc.name)
				if mobile_no:
					send_whatsapp_msg(mobile_no, docket_doc.description + '\nReference: ' + docket_url , docket_doc.doctype, docket_doc.name)

@frappe.whitelist()
def minute_docket_scheduler():
	current_date_time = get_datetime(now())
	dockets = frappe.db.get_all('Docket', filters = { 'status': 'Open', 'remind_before_unit': 'Minutes'})
	if dockets:
		for docket in dockets:
			docket_doc = frappe.get_doc('Docket', docket.name)
			mobile_no = frappe.db.get_value('User', docket_doc.owner, 'mobile_no')
			due_date = get_datetime(docket_doc.due_date)
			docket_url = get_url_to_form(docket_doc.doctype, docket_doc.name)
			docket_due_message_mail = 'Docket '+ docket_doc.name + ' for '+ docket_doc.subject + ' had Overdue on '+ str(docket_doc.due_date)
			docket_due_message_wtsp = 'Docket '+ docket_doc.name + ' for '+ docket_doc.subject + ' had Overdue on *'+ str(docket_doc.due_date) + '*.\nReference : ' + docket_url

			# Changing Status to Overdue
			if due_date < current_date_time:
				change_docket_status(docket_doc)
				create_notification_log(docket_doc.subject + 'is Overdue', docket_doc.owner, docket_due_message_mail, docket_doc.doctype, docket_doc.name)
				if mobile_no:
					send_whatsapp_msg(mobile_no, docket_due_message_wtsp, docket_doc.doctype, docket_doc.name)

			#Minutes Scheduler Checking
			if docket_doc.remind_before_unit == 'Minutes':
				if due_date:
					time_difference = int(time_diff(due_date, current_date_time).total_seconds() / 60)
			if time_difference == docket_doc.remind_before:
				create_notification_log(docket_doc.subject, docket_doc.owner, docket_doc.description, docket_doc.doctype, docket_doc.name)
				if mobile_no:
					send_whatsapp_msg(mobile_no, docket_doc.description+ '\nReference: ' + docket_url, docket_doc.doctype, docket_doc.name)

@frappe.whitelist()
def daily_todo_scheduler():
	todos = frappe.db.get_all('ToDo', filters = {'status': 'Open'})
	if todos:
		for todo in todos:
			todo_doc = frappe.get_doc('ToDo', todo.name)
			today = getdate(frappe.utils.today())
			user = todo_doc.owner
			mobile_no = frappe.db.get_value('User', user, 'mobile_no')
			due_date = getdate(todo_doc.date)
			todo_url = get_url_to_form(todo_doc.doctype, todo_doc.name)
			todo_due_message = 'Your ToDo for *'+ remove_html_tags(todo_doc.description) + '* had Overdue on *'+ str(due_date) + '*.\nReference : ' + todo_url
			if date < today:
				get_over_due_list(self.todo)
				create_notification_log(todo_doc.description, user, todo_due_message, todo_doc.doctype, todo_doc.name)
				if mobile_no:
					send_whatsapp_msg(mobile_no, todo_due_message, todo_doc.doctype, todo_doc.name)

@frappe.whitelist()
def send_whatsapp_msg(mobile_no, message_body, document_type=None, document_name=None):
	whatsapp_communication_doc = frappe.new_doc("WhatsApp Communication")
	whatsapp_communication_doc.to = mobile_no
	whatsapp_communication_doc.message_type = 'Text'
	whatsapp_communication_doc.message_body = message_body
	whatsapp_communication_doc.reference_dt = document_type
	whatsapp_communication_doc.reference_dn = document_name
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
		current_date = get_datetime(now())
		due_date = get_datetime(self.due_date)
		if current_date >= due_date:
			self.status = 'Overdue'
			frappe.db.set_value(self.doctype, self.name, 'status', 'cancelled')
			frappe.db.commit()
#todo
def change_todo_status(name):
	frappe.db.set_value('ToDo', name, 'status', 'Overdue')
	frappe.db.commit()

def todo_after_insert(doc, method):
	user = doc.owner
	mobile_no = frappe.db.get_value('User', user, 'mobile_no')
	todo_url = get_url_to_form(doc.doctype, doc.name)
	whatsapp_msg = "New ToDo Created for you : *" + remove_html_tags(doc.description) + '*. \nReference : ' + todo_url
	if mobile_no:
		send_whatsapp_msg(mobile_no, whatsapp_msg, doc.doctype, doc.name)

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@frappe.whitelist()
def get_over_due_list():
	today = getdate(frappe.utils.today())
	users = get_users_with_role('Docket User')
	for user in users:
		query = """
			SELECT DISTINCT
				name,
				description,
				date
			FROM
				`tabToDo`
			WHERE
				owner = '{user}' AND
				status = 'Open' AND
				date < '{today}'
		""".format(user = str(user), today = today)
		todo_doc_list = frappe.db.sql(query, as_dict = 1)
		todo_list = []
		todo = {}
		if todo_doc_list:
			for todo in todo_doc_list:
				url = get_url_to_form('ToDo', todo.name)
				todo_list.append(remove_html_tags(todo.description) + ' : ' + url)
				todo_due_message = 'Your ToDo for *'+ remove_html_tags(todo.description) + '* had Overdue on *'+ str(todo.date) + '*.\nReference : ' + url
				change_todo_status(todo.name)
				create_notification_log(todo.description, user, todo_due_message, 'ToDo', todo.name)
			mobile_no = frappe.db.get_value('User', user, 'mobile_no')
			if mobile_no:
				todo_due_message = 'Your Overdues are,'
				for todo in todo_list:
					todo_due_message += '\n ' + todo
				send_whatsapp_msg(mobile_no, todo_due_message)
