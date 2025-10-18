# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_setup_instructions():
	"""
	Get step-by-step setup instructions for Postman integration
	"""
	return {
		"postman_api_key": {
			"title": "Get Postman API Key",
			"steps": [
				"1. Go to https://web.postman.co/settings/me/api-keys",
				"2. Click 'Generate API Key'",
				"3. Give it a name (e.g., 'Frappe Integration')",
				"4. Copy the generated API key",
				"5. Paste it in the Postman Settings form",
			],
		},
		"workspace_id": {
			"title": "Find Workspace ID",
			"steps": [
				"1. Go to https://web.postman.co/workspaces",
				"2. Click on your workspace",
				"3. Look at the URL: https://web.postman.co/workspaces/{WORKSPACE_ID}",
				"4. Copy the WORKSPACE_ID from the URL",
				"5. Paste it in the Postman Settings form",
			],
		},
		"collection_id": {
			"title": "Find Collection ID",
			"steps": [
				"1. Go to https://web.postman.co/collections",
				"2. Click on your collection",
				"3. Look at the URL: https://web.postman.co/collections/{COLLECTION_ID}",
				"4. Copy the COLLECTION_ID from the URL",
				"5. Paste it in the Postman Settings form",
			],
		},
	}


@frappe.whitelist()
def get_api_key():
	"""
	Get API key for the current user
	"""
	try:
		user = frappe.get_doc("User", frappe.session.user)
		if not user.api_key:
			user.generate_keys()
			user.save()
		return {"api_key": user.api_key}
	except Exception as e:
		frappe.log_error(f"Error getting API key: {e!s}", "API Key Error")
		return {"error": str(e)}


@frappe.whitelist()
def validate_postman_setup():
	"""
	Validate if Postman setup is complete and working
	"""
	try:
		postman_settings = frappe.get_single("Postman Setting")

		api_key = postman_settings.get_password("postman_api_key")
		checks = {
			"postman_settings_exists": bool(postman_settings.name),
			"api_key_configured": bool(api_key),
			"workspace_id_configured": bool(postman_settings.workspace_id),
			"collection_id_configured": bool(postman_settings.collection_id),
			"base_url_configured": bool(postman_settings.base_url),
			"auto_sync_enabled": postman_settings.enable_auto_sync,
			"status_active": postman_settings.status == "Active",
		}

		all_configured = all(checks.values())

		return {
			"setup_complete": all_configured,
			"checks": checks,
			"message": "Setup complete! APIs will be automatically synced to Postman."
			if all_configured
			else "Please complete the missing configuration items.",
		}

	except Exception as e:
		return {"setup_complete": False, "error": str(e)}


@frappe.whitelist()
def get_doctype_list():
	"""
	Get list of all custom doctypes that can have APIs generated
	"""
	try:
		custom_doctypes = frappe.get_all(
			"DocType", filters={"custom": 1, "istable": 0}, fields=["name", "module", "creation"]
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

		# Filter out system doctypes
		available_doctypes = [dt for dt in custom_doctypes if dt.name not in system_doctypes]

		# Get API Generator status for each doctype
		for doctype in available_doctypes:
			api_gen_exists = frappe.db.exists("API Generator", doctype.name)
			doctype["has_api_generator"] = bool(api_gen_exists)

			if api_gen_exists:
				api_gen = frappe.get_doc("API Generator", doctype.name)
				doctype["api_status"] = api_gen.status
				doctype["auto_generate"] = api_gen.auto_generate

		return {"doctypes": available_doctypes}

	except Exception as e:
		frappe.log_error(f"Error getting doctype list: {e!s}", "DocType List Error")
		return {"error": str(e)}


@frappe.whitelist()
def get_system_status():
	"""
	Get overall system status and statistics
	"""
	try:
		# Count API Generators
		total_api_generators = frappe.db.count("API Generator")
		active_api_generators = frappe.db.count("API Generator", filters={"status": "Active"})

		# Count custom doctypes
		total_custom_doctypes = frappe.db.count("DocType", filters={"custom": 1, "istable": 0})

		# Count whitelisted methods
		from frappe_postman_sync.whitelist_scanner import scan_all_whitelisted_methods

		all_whitelisted_methods = scan_all_whitelisted_methods()
		total_whitelisted_methods = sum(len(methods) for methods in all_whitelisted_methods.values())

		# Postman Settings status
		postman_settings = frappe.get_single("Postman Setting")
		api_key = postman_settings.get_password("postman_api_key")
		postman_configured = bool(
			api_key and postman_settings.workspace_id and postman_settings.collection_id
		)

		return {
			"total_custom_doctypes": total_custom_doctypes,
			"total_api_generators": total_api_generators,
			"active_api_generators": active_api_generators,
			"total_whitelisted_methods": total_whitelisted_methods,
			"whitelisted_methods_by_app": all_whitelisted_methods,
			"postman_configured": postman_configured,
			"postman_status": postman_settings.status if postman_settings.name else "Not Configured",
			"auto_sync_enabled": postman_settings.enable_auto_sync if postman_settings.name else False,
			"last_sync": postman_settings.last_sync if postman_settings.name else None,
		}

	except Exception as e:
		frappe.log_error(f"Error getting system status: {e!s}", "System Status Error")
		return {"error": str(e)}


@frappe.whitelist()
def scan_and_sync_whitelisted_methods():
	"""
	Scan for all whitelisted methods and sync them to Postman
	"""
	try:
		from frappe_postman_sync.whitelist_scanner import sync_whitelisted_methods_to_postman

		result = sync_whitelisted_methods_to_postman()
		return result
	except Exception as e:
		frappe.log_error(f"Error scanning and syncing whitelisted methods: {e!s}", "Whitelist Scan Error")
		return {"status": "error", "message": str(e)}
