# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt


import frappe
import requests


def get_postman_api_key_instructions():
    """
    Get instructions for obtaining Postman API key
    """
    return {
        "title": "How to get your Postman API Key",
        "steps": [
            "1. Go to https://web.postman.co/settings/me/api-keys",
            "2. Click 'Generate API Key'",
            "3. Give it a name (e.g., 'Frappe Integration')",
            "4. Copy the generated API key",
            "5. Paste it in the Postman Settings form",
        ],
    }


def get_workspace_id_instructions():
    """
    Get instructions for finding Postman Workspace ID
    """
    return {
        "title": "How to find your Postman Workspace ID",
        "steps": [
            "1. Go to https://web.postman.co/workspaces",
            "2. Click on your workspace",
            "3. Look at the URL: https://web.postman.co/workspaces/{WORKSPACE_ID}",
            "4. Copy the WORKSPACE_ID from the URL",
            "5. Paste it in the Postman Settings form",
        ],
    }


def get_collection_id_instructions():
    """
    Get instructions for finding Postman Collection ID
    """
    return {
        "title": "How to find your Postman Collection ID",
        "steps": [
            "1. Go to https://web.postman.co/collections",
            "2. Click on your collection",
            "3. Look at the URL: https://web.postman.co/collections/{COLLECTION_ID}",
            "4. Copy the COLLECTION_ID from the URL",
            "5. Paste it in the Postman Settings form",
        ],
    }


def validate_postman_credentials(api_key, workspace_id, collection_id):
    """
    Validate Postman credentials without creating a record
    """
    try:
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

        # Test workspace access
        workspace_url = f"https://api.getpostman.com/workspaces/{workspace_id}"
        workspace_response = requests.get(workspace_url, headers=headers, timeout=10)

        if workspace_response.status_code != 200:
            return {"valid": False, "message": "Invalid workspace ID or API key"}

        # Test collection access
        collection_url = f"https://api.getpostman.com/collections/{collection_id}"
        collection_response = requests.get(collection_url, headers=headers, timeout=10)

        if collection_response.status_code != 200:
            return {
                "valid": False,
                "message": "Invalid collection ID or insufficient permissions",
            }

        return {"valid": True, "message": "Credentials are valid"}

    except Exception as e:
        return {"valid": False, "message": f"Error validating credentials: {e!s}"}


def get_site_info():
    """
    Get site information for Postman environment setup
    """
    try:
        site_config = frappe.get_site_config()
        return {
            "site_name": site_config.get("site_name", "localhost"),
            "site_url": site_config.get("site_url", "http://localhost:8000"),
            "api_key_instructions": "Generate API key from User Settings > API Access",
        }
    except Exception as e:
        frappe.log_error(f"Error getting site info: {e!s}", "Site Info Error")
        return None


def create_sample_postman_collection():
    """
    Create a sample Postman collection structure
    """
    return {
        "info": {
            "name": "Frappe CRUD APIs",
            "description": "Auto-generated CRUD APIs for Frappe doctypes",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000", "type": "string"},
            {"key": "api_key", "value": "{{your_api_key}}", "type": "string"},
        ],
    }


def get_api_key_from_user():
    """
    Get API key for the current user
    """
    try:
        user = frappe.get_doc("User", frappe.session.user)
        if user.api_key:
            return user.api_key
        else:
            # Generate API key if not exists
            user.generate_keys()
            return user.api_key
    except Exception as e:
        frappe.log_error(f"Error getting API key: {e!s}", "API Key Error")
        return None


def format_api_endpoint_for_postman(endpoint, base_url):
    """
    Format API endpoint for Postman collection
    """
    return {
        "name": f"{endpoint['method']} {endpoint['path']}",
        "request": {
            "method": endpoint["method"],
            "header": [
                {"key": "Content-Type", "value": "application/json"},
                {"key": "Authorization", "value": "token {{api_key}}"},
            ],
            "url": {
                "raw": f"{{{{base_url}}}}{endpoint['path']}",
                "host": ["{{base_url}}"],
                "path": endpoint["path"].split("/")[1:]
                if endpoint["path"].startswith("/")
                else endpoint["path"].split("/"),
            },
            "description": endpoint.get("description", ""),
        },
        "response": [],
    }


def get_doctype_fields_for_api(doctype_name):
    """
    Get field information for API documentation
    """
    try:
        meta = frappe.get_meta(doctype_name)
        fields = []

        for field in meta.fields:
            if not field.hidden and not field.is_virtual:
                field_info = {
                    "fieldname": field.fieldname,
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                    "required": field.reqd,
                    "read_only": field.read_only,
                    "description": field.description,
                }

                if field.fieldtype in ["Link", "Select"]:
                    field_info["options"] = field.options
                elif field.fieldtype in ["Int", "Float", "Currency"]:
                    field_info["type"] = "number"
                elif field.fieldtype == "Date":
                    field_info["type"] = "date"
                elif field.fieldtype == "Datetime":
                    field_info["type"] = "datetime"
                else:
                    field_info["type"] = "string"

                fields.append(field_info)

        return fields

    except Exception as e:
        frappe.log_error(
            f"Error getting fields for {doctype_name}: {e!s}", "Field Info Error"
        )
        return []


def create_postman_environment_variables():
    """
    Create Postman environment variables
    """
    return [
        {
            "key": "base_url",
            "value": frappe.get_site_config().get("site_url", "http://localhost:8000"),
            "type": "default",
            "enabled": True,
        },
        {
            "key": "api_key",
            "value": "{{your_api_key}}",
            "type": "secret",
            "enabled": True,
        },
        {
            "key": "site_name",
            "value": frappe.get_site_config().get("site_name", "localhost"),
            "type": "default",
            "enabled": True,
        },
    ]
