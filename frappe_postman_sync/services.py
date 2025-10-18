# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.utils import now_datetime


def auto_generate_api_for_doctype(doc, method=None):
	"""
	Automatically generate API endpoints for a newly created doctype
	This function is called from hooks when a new doctype is created
	"""
	try:
		doctype_name = doc.name

		# Check if API generator already exists for this doctype
		existing = frappe.db.exists(
			"API Generator", {"doctype_name": doctype_name, "generation_type": "Single DocType"}
		)
		if existing:
			frappe.log_error(f"API Generator already exists for {doctype_name}", "API Generation")
			return

		# Check if doctype exists and is not a system doctype
		if not frappe.db.exists("DocType", doctype_name):
			frappe.log_error(f"DocType {doctype_name} does not exist", "API Generation")
			return

		# Skip system doctypes
		system_doctypes = [
			"DocType",
			"DocField",
			"Custom Field",
			"Property Setter",
			"Custom DocPerm",
			"User",
			"Role",
			"Permission",
			"Has Role",
			"Communication",
			"Version",
			"Error Log",
			"Activity Log",
			"File",
			"ToDo",
			"Comment",
			"Assignment",
			"Tag",
			"Tag Link",
		]

		if doctype_name in system_doctypes:
			frappe.log_error(f"Skipping system doctype {doctype_name}", "API Generation")
			return

		# Create API Generator record
		api_gen = frappe.get_doc(
			{
				"doctype": "API Generator",
				"generation_type": "Single DocType",
				"doctype_name": doctype_name,
				"auto_generate": 1,
				"created_by_doctype": 1,
				"status": "Active",
			}
		)

		api_gen.insert(ignore_permissions=True)
		frappe.db.commit()

		frappe.log_error(f"Auto-generated API endpoints for {doctype_name}", "API Generation")

	except Exception as e:
		frappe.log_error(f"Error auto-generating API for {doctype_name}: {e!s}", "API Generation Error")


def sync_existing_doctypes():
	"""
	Sync existing doctypes that don't have API generators
	This can be called manually or during app installation
	"""
	try:
		# Get all custom doctypes
		custom_doctypes = frappe.get_all(
			"DocType", filters={"custom": 1, "istable": 0}, fields=["name", "module"]
		)

		system_doctypes = [
			"DocType",
			"DocField",
			"Custom Field",
			"Property Setter",
			"Custom DocPerm",
			"User",
			"Role",
			"Permission",
			"Has Role",
			"Communication",
			"Version",
			"Error Log",
			"Activity Log",
			"File",
			"ToDo",
			"Comment",
			"Assignment",
			"Tag",
			"Tag Link",
			"API Generator",
			"Postman Settings",
		]

		created_count = 0

		for doctype in custom_doctypes:
			# Skip system doctypes
			if doctype.name in system_doctypes:
				continue

			# Check if API generator already exists
			existing = frappe.db.exists("API Generator", doctype.name)
			if existing:
				continue

			# Create API Generator
			api_gen = frappe.get_doc(
				{
					"doctype": "API Generator",
					"doctype_name": doctype.name,
					"auto_generate": 1,
					"created_by_doctype": 0,
					"status": "Active",
				}
			)

			api_gen.insert(ignore_permissions=True)
			created_count += 1

		frappe.db.commit()
		frappe.msgprint(f"Created API generators for {created_count} existing doctypes")

	except Exception as e:
		frappe.log_error(f"Error syncing existing doctypes: {e!s}", "API Sync Error")


def get_api_documentation(doctype_name):
	"""
	Get comprehensive API documentation for a doctype
	"""
	try:
		api_gen = frappe.get_doc("API Generator", doctype_name)
		doctype_meta = frappe.get_meta(doctype_name)

		# Parse API endpoints
		api_endpoints = (
			json.loads(api_gen.api_endpoints)
			if isinstance(api_gen.api_endpoints, str)
			else api_gen.api_endpoints
		)

		# Get field information
		fields_info = []
		for field in doctype_meta.fields:
			if not field.hidden:
				fields_info.append(
					{
						"fieldname": field.fieldname,
						"label": field.label,
						"fieldtype": field.fieldtype,
						"required": field.reqd,
						"read_only": field.read_only,
						"options": field.options if field.fieldtype in ["Link", "Select"] else None,
					}
				)

		documentation = {
			"doctype": doctype_name,
			"module": doctype_meta.module,
			"description": doctype_meta.description or f"API endpoints for {doctype_name}",
			"fields": fields_info,
			"endpoints": api_endpoints,
			"authentication": {
				"type": "Bearer Token",
				"header": "Authorization: token <your_api_key>",
				"description": "Include your API key in the Authorization header",
			},
			"base_url": frappe.get_site_config().get("site_url", "http://localhost:8000"),
			"examples": {
				"create_record": {
					"method": "POST",
					"url": f"/api/resource/{doctype_name}",
					"headers": {"Content-Type": "application/json", "Authorization": "token <your_api_key>"},
					"body": {"field_name": "field_value"},
				},
				"get_records": {
					"method": "GET",
					"url": f"/api/resource/{doctype_name}",
					"headers": {"Authorization": "token <your_api_key>"},
				},
			},
		}

		return documentation

	except Exception as e:
		frappe.log_error(
			f"Error getting API documentation for {doctype_name}: {e!s}", "API Documentation Error"
		)
		return None


@frappe.whitelist()
def generate_api_for_doctype(doctype_name):
	"""
	Manually generate API for a specific doctype
	"""
	try:
		auto_generate_api_for_doctype(doctype_name)
		return {"status": "success", "message": f"API generated for {doctype_name}"}
	except Exception as e:
		return {"status": "error", "message": str(e)}


@frappe.whitelist()
def bulk_generate_apis(doctype_list):
	"""
	Bulk generate APIs for multiple doctypes
	"""
	try:
		doctypes = json.loads(doctype_list) if isinstance(doctype_list, str) else doctype_list
		results = []

		for doctype_name in doctypes:
			try:
				auto_generate_api_for_doctype(doctype_name)
				results.append({"doctype": doctype_name, "status": "success"})
			except Exception as e:
				results.append({"doctype": doctype_name, "status": "error", "message": str(e)})

		return {"status": "completed", "results": results}

	except Exception as e:
		return {"status": "error", "message": str(e)}
