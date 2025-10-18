# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import json

import frappe
import requests
from frappe.model.document import Document
from frappe.utils import now_datetime


class PostmanSetting(Document):
	def validate(self):
		if self.enable_auto_sync:
			self.validate_postman_connection()

	@frappe.whitelist()
	def validate_postman_connection(self):
		"""Validate Postman API connection"""
		try:
			api_key = self.get_password("postman_api_key")
			headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

			# Test connection by fetching workspace info
			url = f"https://api.getpostman.com/workspaces/{self.workspace_id}"
			response = requests.get(url, headers=headers, timeout=10)

			if response.status_code == 200:
				self.status = "Active"
				frappe.msgprint("Postman connection successful!")
			else:
				self.status = "Error"
				frappe.throw(f"Failed to connect to Postman API. Status: {response.status_code}")

		except Exception as e:
			self.status = "Error"
			frappe.throw(f"Error validating Postman connection: {e!s}")

	@frappe.whitelist()
	def sync_to_postman(self):
		"""Sync all generated APIs to Postman"""
		if not self.enable_auto_sync:
			return

		try:
			api_generators = frappe.get_all(
				"API Generator",
				filters={"status": "Active"},
				fields=["name", "doctype_name", "generation_type", "api_endpoints"],
			)

			for api_gen in api_generators:
				self.create_postman_collection_items(api_gen)

			self.last_sync = now_datetime()
			self.save()
			frappe.msgprint("Successfully synced APIs to Postman")

		except Exception as e:
			frappe.log_error(f"Postman sync error: {e!s}", "Postman Sync Error")
			frappe.throw(f"Failed to sync to Postman: {e!s}")

	def create_postman_collection_items(self, api_generator):
		"""Create collection items for a specific doctype's APIs"""
		try:
			api_key = self.get_password("postman_api_key")
			headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

			# Parse API endpoints from JSON string
			api_endpoints = (
				json.loads(api_generator.api_endpoints)
				if isinstance(api_generator.api_endpoints, str)
				else api_generator.api_endpoints
			)

			# Handle both single doctype and module generation
			if api_generator.generation_type == "Entire Module":
				# For module generation, api_endpoints is a dict with doctype names as keys
				for doctype_name, endpoints in api_endpoints.items():
					for endpoint in endpoints:
						item_data = self.build_postman_item(endpoint, doctype_name)
						self._create_postman_request(item_data, headers)
			else:
				# For single doctype generation, api_endpoints is a list
				for endpoint in api_endpoints:
					item_data = self.build_postman_item(endpoint, api_generator.doctype_name)
					self._create_postman_request(item_data, headers)

		except Exception as e:
			frappe.log_error(f"Error creating Postman collection items: {e!s}", "Postman Sync Error")

	def _create_postman_request(self, item_data, headers):
		"""Helper method to create a single Postman request"""
		try:
			url = f"https://api.getpostman.com/collections/{self.collection_id}/requests"
			response = requests.post(url, headers=headers, json=item_data, timeout=10)

			if response.status_code not in [200, 201]:
				frappe.log_error(f"Failed to create Postman item: {response.text}", "Postman API Error")

		except Exception as e:
			frappe.log_error(f"Error creating Postman request: {e!s}", "Postman Sync Error")

	def build_postman_item(self, endpoint, doctype_name):
		"""Build Postman item data structure"""
		# Handle custom method naming
		if endpoint.get("custom_method"):
			item_name = f"{endpoint['method']} {endpoint.get('method_name', 'Custom Method')}"
		else:
			item_name = f"{endpoint['method']} {endpoint['path']}"

		# Build request body for POST/PUT requests
		request_body = None
		if endpoint["method"] in ["POST", "PUT", "PATCH"]:
			# Different body structure for custom methods
			if endpoint.get("custom_method"):
				request_body = {
					"mode": "raw",
					"raw": json.dumps({"args": ["arg1", "arg2"], "kwargs": {"key": "value"}}, indent=2),
					"options": {"raw": {"language": "json"}},
				}
			else:
				# Generate body with actual DocType fields
				body_data = self.get_doctype_fields_template(doctype_name)
				request_body = {
					"mode": "raw",
					"raw": json.dumps(body_data, indent=2),
					"options": {"raw": {"language": "json"}},
				}

		# Build URL with query parameters - Fixed format for Postman API
		base_url_clean = self.base_url.rstrip("/")
		endpoint_path = endpoint["path"].lstrip("/")
		full_url = f"{base_url_clean}/{endpoint_path}"

		# Parse URL components
		from urllib.parse import parse_qs, urlparse

		parsed_url = urlparse(full_url)

		# Extract path segments (remove empty strings)
		path_segments = [seg for seg in parsed_url.path.split("/") if seg]

		url_data = {
			"raw": full_url,
			"protocol": parsed_url.scheme or "http",
			"host": [parsed_url.netloc] if parsed_url.netloc else [],
			"path": path_segments,
		}

		# Add query parameters if they exist
		if parsed_url.query:
			query_params = []
			for key, values in parse_qs(parsed_url.query).items():
				for value in values:
					query_params.append({"key": key, "value": value})
			url_data["query"] = query_params

		# Enhanced description for custom methods
		description = f"Auto-generated API for {doctype_name} doctype"
		if endpoint.get("custom_method"):
			description += f"\n\nCustom Method: {endpoint.get('method_name', 'Unknown')}"
			description += f"\nPath: {endpoint['path']}"
			if endpoint.get("parameters"):
				description += "\n\nParameters:"
				for param in endpoint["parameters"]:
					description += f"\n- {param['name']} ({param['type']}): {param['description']}"

		return {
			"name": item_name,
			"request": {
				"method": endpoint["method"],
				"header": [
					{"key": "Content-Type", "value": "application/json"},
					{"key": "Authorization", "value": "token {{api_key}}"},
				],
				"url": url_data,
				"body": request_body,
				"description": description,
			},
		}

	def get_doctype_fields_template(self, doctype_name):
		"""Generate JSON template with all DocType fields for request body"""
		try:
			# Get DocType meta information
			doctype_meta = frappe.get_meta(doctype_name)

			# Create template with all fields
			template = {}

			# Add only essential standard fields (exclude auditable/system fields)
			essential_fields = {
				"doctype": doctype_name,
				"name": "",  # Only include if user wants to specify custom name
			}

			# Add essential fields to template
			for field_name, default_value in essential_fields.items():
				template[field_name] = default_value

			# Add custom fields from DocType (exclude system/auditable fields)
			excluded_fieldtypes = ["Section Break", "Column Break", "Tab Break", "HTML", "Button"]

			# Fields that are system-managed and should not be in request body
			excluded_fieldnames = [
				"creation",
				"modified",
				"modified_by",
				"owner",
				"docstatus",
				"idx",
				"amended_from",
				"creation_date",
				"modified_date",
				"user",
				"user_type",
				"last_login",
				"login_after",
				"logout_time",
				"last_ip",
				"last_login_ip",
				"user_type",
				"api_key",
				"api_secret",
			]

			for field in doctype_meta.fields:
				if (
					field.fieldtype not in excluded_fieldtypes
					and field.fieldname not in excluded_fieldnames
					and not field.read_only
				):  # Exclude read-only fields
					field_name = field.fieldname

					# Set appropriate default values based on field type
					if field.fieldtype == "Data":
						template[field_name] = ""
					elif field.fieldtype == "Text":
						template[field_name] = ""
					elif field.fieldtype == "Small Text":
						template[field_name] = ""
					elif field.fieldtype == "Long Text":
						template[field_name] = ""
					elif field.fieldtype == "Int":
						template[field_name] = 0
					elif field.fieldtype == "Float":
						template[field_name] = 0.0
					elif field.fieldtype == "Currency":
						template[field_name] = 0.0
					elif field.fieldtype == "Percent":
						template[field_name] = 0.0
					elif field.fieldtype == "Check":
						template[field_name] = 0
					elif field.fieldtype == "Select":
						template[field_name] = ""
					elif field.fieldtype == "Link":
						template[field_name] = ""
					elif field.fieldtype == "Dynamic Link":
						template[field_name] = ""
					elif field.fieldtype == "Date":
						template[field_name] = ""
					elif field.fieldtype == "Datetime":
						template[field_name] = ""
					elif field.fieldtype == "Time":
						template[field_name] = ""
					elif field.fieldtype == "Table":
						template[field_name] = []
					elif field.fieldtype == "Attach":
						template[field_name] = ""
					elif field.fieldtype == "Attach Image":
						template[field_name] = ""
					elif field.fieldtype == "Barcode":
						template[field_name] = ""
					elif field.fieldtype == "Code":
						template[field_name] = ""
					elif field.fieldtype == "Color":
						template[field_name] = ""
					elif field.fieldtype == "Geolocation":
						template[field_name] = {"latitude": 0.0, "longitude": 0.0}
					elif field.fieldtype == "Duration":
						template[field_name] = 0
					elif field.fieldtype == "Rating":
						template[field_name] = 0
					elif field.fieldtype == "Signature":
						template[field_name] = ""
					elif field.fieldtype == "Password":
						template[field_name] = ""
					elif field.fieldtype == "Read Only":
						template[field_name] = ""
					else:
						# Default to empty string for unknown field types
						template[field_name] = ""

			return template

		except Exception as e:
			# Fallback to basic template if there's an error
			frappe.log_error(
				f"Error generating DocType template for {doctype_name}: {e!s}", "DocType Template Error"
			)
			return {
				"doctype": doctype_name,
				"name": "",
				"field1": "",
				"field2": "",
				"field3": "",
			}
