# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import json

import frappe
import requests
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def sync_all_apis_to_postman():
	"""
	Sync all generated APIs to Postman
	"""
	try:
		postman_settings = frappe.get_single("Postman Setting")

		if not postman_settings.enable_auto_sync:
			return {"status": "error", "message": "Auto sync is disabled"}

		if postman_settings.status != "Active":
			return {"status": "error", "message": "Postman settings are not active"}

		postman_settings.sync_to_postman()

		return {
			"status": "success",
			"message": "All APIs synced to Postman successfully",
			"last_sync": postman_settings.last_sync,
		}

	except Exception as e:
		frappe.log_error(f"Error syncing APIs to Postman: {e!s}", "Postman Sync Error")
		return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_postman_collection_info():
	"""
	Get information about the Postman collection
	"""
	try:
		postman_settings = frappe.get_single("Postman Setting")

		api_key = postman_settings.get_password("postman_api_key")
		headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

		# Get collection details
		url = f"https://api.getpostman.com/collections/{postman_settings.collection_id}"
		response = requests.get(url, headers=headers, timeout=10)

		if response.status_code == 200:
			collection_data = response.json()
			return {
				"status": "success",
				"collection": {
					"name": collection_data.get("collection", {}).get("name"),
					"id": collection_data.get("collection", {}).get("id"),
					"item_count": len(collection_data.get("collection", {}).get("item", [])),
					"updated_at": collection_data.get("collection", {}).get("updatedAt"),
				},
			}
		else:
			return {"status": "error", "message": f"Failed to fetch collection info: {response.status_code}"}

	except Exception as e:
		frappe.log_error(f"Error getting Postman collection info: {e!s}", "Postman API Error")
		return {"status": "error", "message": str(e)}


@frappe.whitelist()
def create_postman_environment():
	"""
	Create a Postman environment for the Frappe site
	"""
	try:
		postman_settings = frappe.get_single("Postman Setting")

		api_key = postman_settings.get_password("postman_api_key")
		headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

		# Create environment data
		environment_data = {
			"environment": {
				"name": f"Frappe - {frappe.get_site_config().get('site_name', 'Local')}",
				"values": [
					{"key": "base_url", "value": postman_settings.base_url, "enabled": True},
					{
						"key": "api_key",
						"value": "{{your_api_key}}",
						"enabled": True,
						"description": "Your Frappe API key",
					},
					{
						"key": "site_name",
						"value": frappe.get_site_config().get("site_name", "localhost"),
						"enabled": True,
					},
				],
			}
		}

		# Create environment in Postman
		url = "https://api.getpostman.com/environments"
		response = requests.post(url, headers=headers, json=environment_data, timeout=10)

		if response.status_code in [200, 201]:
			env_data = response.json()
			return {
				"status": "success",
				"message": "Postman environment created successfully",
				"environment_id": env_data.get("environment", {}).get("id"),
			}
		else:
			return {"status": "error", "message": f"Failed to create environment: {response.status_code}"}

	except Exception as e:
		frappe.log_error(f"Error creating Postman environment: {e!s}", "Postman API Error")
		return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_api_documentation_html(doctype_name):
	"""
	Generate HTML documentation for API endpoints
	"""
	try:
		from frappe_postman_sync.services import get_api_documentation

		doc = get_api_documentation(doctype_name)
		if not doc:
			return {"status": "error", "message": "Failed to generate documentation"}

		html = f"""
		<div class="api-documentation">
			<h2>{doc['doctype']} API Documentation</h2>
			<p><strong>Module:</strong> {doc['module']}</p>
			<p><strong>Description:</strong> {doc['description']}</p>
			<p><strong>Base URL:</strong> {doc['base_url']}</p>

			<h3>Authentication</h3>
			<p><strong>Type:</strong> {doc['authentication']['type']}</p>
			<p><strong>Header:</strong> <code>{doc['authentication']['header']}</code></p>

			<h3>Fields</h3>
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>Field Name</th>
						<th>Label</th>
						<th>Type</th>
						<th>Required</th>
						<th>Options</th>
					</tr>
				</thead>
				<tbody>
		"""

		for field in doc["fields"]:
			html += f"""
					<tr>
						<td>{field['fieldname']}</td>
						<td>{field['label']}</td>
						<td>{field['fieldtype']}</td>
						<td>{'Yes' if field['required'] else 'No'}</td>
						<td>{field['options'] or '-'}</td>
					</tr>
			"""

		html += """
				</tbody>
			</table>

			<h3>API Endpoints</h3>
		"""

		for endpoint in doc["endpoints"]:
			html += f"""
			<div class="endpoint">
				<h4><span class="method {endpoint['method'].lower()}">{endpoint['method']}</span> {endpoint['path']}</h4>
				<p><strong>Description:</strong> {endpoint['description']}</p>
			"""

			if endpoint.get("parameters"):
				html += "<h5>Parameters:</h5><ul>"
				for param in endpoint["parameters"]:
					required = " (Required)" if param.get("required") else ""
					html += f"<li><strong>{param['name']}</strong> ({param['type']}){required}: {param['description']}</li>"
				html += "</ul>"

			html += "</div>"

		html += """
			<h3>Examples</h3>
			<div class="example">
				<h4>Create Record</h4>
				<pre><code>
POST {base_url}/api/resource/{doctype_name}
Content-Type: application/json
Authorization: token &lt;your_api_key&gt;

{
	"field_name": "field_value"
}
				</code></pre>
			</div>
		</div>
		"""

		return {"status": "success", "html": html}

	except Exception as e:
		frappe.log_error(f"Error generating HTML documentation: {e!s}", "API Documentation Error")
		return {"status": "error", "message": str(e)}
