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
                frappe.throw(
                    f"Failed to connect to Postman API. Status: {response.status_code}"
                )

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
                fields=[
                    "name",
                    "doctype_name",
                    "generation_type",
                    "api_endpoints",
                    "collection_title",
                ],
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

            # Update collection name if collection_title is provided
            if api_generator.get("collection_title"):
                self.update_postman_collection_name(
                    api_generator["collection_title"], headers
                )

            # Parse API endpoints from JSON string
            api_endpoints = (
                json.loads(api_generator.api_endpoints)
                if isinstance(api_generator.api_endpoints, str)
                else api_generator.api_endpoints
            )

            # Build all collection items organized by folders
            collection_items = []

            # Handle both single doctype and module generation
            if api_generator.generation_type == "Entire Module":
                # Get the module name from the API generator
                module_name = api_generator.module_name

                # Only create a module folder if module_name is properly set
                if module_name and module_name != "Unknown Module":
                    module_folder = {
                        "name": f"{module_name} Module",
                        "description": f"APIs for {module_name} module",
                        "item": [],
                    }

                    # For module generation, api_endpoints is a dict with doctype names as keys
                    for doctype_name, endpoints in api_endpoints.items():
                        # Create a subfolder for each DocType within the module
                        doctype_folder = {
                            "name": doctype_name,
                            "description": f"APIs for {doctype_name} DocType",
                            "item": [],
                        }

                        for endpoint in endpoints:
                            item_data = self.build_postman_item(endpoint, doctype_name)
                            doctype_folder["item"].append(item_data)

                        module_folder["item"].append(doctype_folder)

                    collection_items.append(module_folder)
                else:
                    # If module name is not set or is "Unknown Module", create DocType folders directly
                    # without the outer module folder
                    for doctype_name, endpoints in api_endpoints.items():
                        doctype_folder = {
                            "name": doctype_name,
                            "description": f"APIs for {doctype_name} DocType",
                            "item": [],
                        }

                        for endpoint in endpoints:
                            item_data = self.build_postman_item(endpoint, doctype_name)
                            doctype_folder["item"].append(item_data)

                        collection_items.append(doctype_folder)
            else:
                # For single doctype generation, create a folder for the DocType
                doctype_folder = {
                    "name": api_generator.doctype_name,
                    "description": f"APIs for {api_generator.doctype_name} DocType",
                    "item": [],
                }

                for endpoint in api_endpoints:
                    item_data = self.build_postman_item(
                        endpoint, api_generator.doctype_name
                    )
                    doctype_folder["item"].append(item_data)

                collection_items.append(doctype_folder)

            # Update the entire collection at once
            self._update_postman_collection(collection_items, headers)

        except Exception as e:
            frappe.log_error(
                f"Error creating Postman collection items: {e!s}", "Postman Sync Error"
            )

    def _update_postman_collection(self, collection_items, headers):
        """Helper method to append new items to Postman collection (preserves existing items)"""
        try:
            # Get current collection
            url = f"https://api.getpostman.com/collections/{self.collection_id}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                frappe.log_error(
                    f"Failed to fetch collection: {response.text}",
                    "Postman API Error",
                )
                return

            collection_data = response.json()
            collection_info = collection_data.get("collection", {})

            # Get existing items
            existing_items = collection_info.get("item", [])

            # Process new items - replace existing folders to ensure only one folder per type
            final_items = []

            # Get all folder names from new items
            new_folder_names = {item.get("name", "") for item in collection_items}

            # Keep existing folders that are not being replaced
            for existing_item in existing_items:
                existing_folder_name = existing_item.get("name", "")
                if existing_folder_name not in new_folder_names:
                    final_items.append(existing_item)

            # Add all new folders (replacing any existing ones with same name)
            final_items.extend(collection_items)

            # Always update the collection to ensure proper folder structure
            collection_info["item"] = final_items

            # Update the collection
            update_payload = {"collection": collection_info}
            update_response = requests.put(
                url, headers=headers, json=update_payload, timeout=10
            )

            if update_response.status_code not in [200, 201]:
                frappe.log_error(
                    f"Failed to update collection: {update_response.text}",
                    "Postman API Error",
                )
            else:
                frappe.msgprint(
                    f"Updated Postman collection with {len(collection_items)} folders"
                )

        except Exception as e:
            frappe.log_error(
                f"Error updating Postman collection: {e!s}", "Postman Sync Error"
            )

    def update_postman_collection_name(self, collection_title, headers):
        """Update the Postman collection name"""
        try:
            url = f"https://api.getpostman.com/collections/{self.collection_id}"

            # Get current collection
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                frappe.log_error(
                    f"Failed to fetch collection for name update: {response.text}",
                    "Postman API Error",
                )
                return

            collection_data = response.json()
            collection_info = collection_data.get("collection", {})

            # Update the collection name
            collection_info["info"]["name"] = collection_title

            # Update the collection
            update_payload = {"collection": collection_info}
            update_response = requests.put(
                url, headers=headers, json=update_payload, timeout=10
            )

            if update_response.status_code not in [200, 201]:
                frappe.log_error(
                    f"Failed to update collection name: {update_response.text}",
                    "Postman API Error",
                )
            else:
                frappe.msgprint(
                    f"Updated Postman collection name to: {collection_title}"
                )

        except Exception as e:
            frappe.log_error(
                f"Error updating Postman collection name: {e!s}", "Postman Sync Error"
            )

    def sync_single_api_generator_optimized(self, api_generator):
        """
        OPTIMIZED sync for a single API generator - makes only 2 API calls total!
        This is the key optimization that reduces sync time from 6+ minutes to seconds.
        """
        try:
            api_key = self.get_password("postman_api_key")
            headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

            # Get current collection in ONE API call
            url = f"https://api.getpostman.com/collections/{self.collection_id}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                frappe.log_error(
                    f"Failed to fetch collection: {response.text}",
                    "Postman API Error",
                )
                return

            collection_data = response.json()
            collection_info = collection_data.get("collection", {})

            # Update collection name if provided
            if api_generator.get("collection_title"):
                collection_info["info"]["name"] = api_generator["collection_title"]

            # Parse API endpoints
            api_endpoints = (
                json.loads(api_generator.api_endpoints)
                if isinstance(api_generator.api_endpoints, str)
                else api_generator.api_endpoints
            )

            # Build collection items efficiently
            new_items = self._build_collection_items_fast(api_generator, api_endpoints)

            # Get existing items and merge efficiently
            existing_items = collection_info.get("item", [])
            final_items = self._merge_collection_items_fast(existing_items, new_items)

            # Update collection ready for single API call
            collection_info["item"] = final_items
            update_payload = {"collection": collection_info}

            # Update collection in ONE API call
            update_response = requests.put(
                url, headers=headers, json=update_payload, timeout=10
            )

            if update_response.status_code not in [200, 201]:
                frappe.log_error(
                    f"Failed to update collection: {update_response.text}",
                    "Postman API Error",
                )
            else:
                print(
                    f"✅ Optimized sync complete: {len(new_items)} folders updated in 2 API calls"
                )

        except Exception as e:
            frappe.log_error(
                f"Error in optimized sync: {e!s}", "Optimized Postman Sync Error"
            )

    def _build_collection_items_fast(self, api_generator, api_endpoints):
        """Build collection items efficiently without multiple API calls"""
        collection_items = []

        if api_generator.generation_type == "Entire Module":
            module_name = api_generator.module_name

            if module_name and module_name != "Unknown Module":
                # Create module folder with all DocType subfolders
                module_folder = {
                    "name": f"{module_name} Module",
                    "description": f"APIs for {module_name} module",
                    "item": [],
                }

                for doctype_name, endpoints in api_endpoints.items():
                    doctype_folder = {
                        "name": doctype_name,
                        "description": f"APIs for {doctype_name} DocType",
                        "item": [],
                    }

                    for endpoint in endpoints:
                        item_data = self.build_postman_item(endpoint, doctype_name)
                        doctype_folder["item"].append(item_data)

                    module_folder["item"].append(doctype_folder)

                collection_items.append(module_folder)
            else:
                # Create DocType folders directly
                for doctype_name, endpoints in api_endpoints.items():
                    doctype_folder = {
                        "name": doctype_name,
                        "description": f"APIs for {doctype_name} DocType",
                        "item": [],
                    }

                    for endpoint in endpoints:
                        item_data = self.build_postman_item(endpoint, doctype_name)
                        doctype_folder["item"].append(item_data)

                    collection_items.append(doctype_folder)
        else:
            # Single DocType
            doctype_folder = {
                "name": api_generator.doctype_name,
                "description": f"APIs for {api_generator.doctype_name} DocType",
                "item": [],
            }

            for endpoint in api_endpoints:
                item_data = self.build_postman_item(
                    endpoint, api_generator.doctype_name
                )
                doctype_folder["item"].append(item_data)

            collection_items.append(doctype_folder)

        return collection_items

    def _merge_collection_items_fast(self, existing_items, new_items):
        """Merge collection items efficiently and prevent duplicates"""
        # Get folder names from new items
        new_folder_names = {item.get("name", "") for item in new_items}

        # Keep existing folders that are not being replaced
        final_items = []
        for existing_item in existing_items:
            existing_folder_name = existing_item.get("name", "")
            if existing_folder_name not in new_folder_names:
                final_items.append(existing_item)

        # Add all new folders (replacing any existing ones with same name)
        final_items.extend(new_items)

        return final_items

    @frappe.whitelist()
    def clear_postman_collection(self):
        """Clear all items from Postman collection"""
        try:
            api_key = self.get_password("postman_api_key")
            headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

            # Get current collection
            url = f"https://api.getpostman.com/collections/{self.collection_id}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                frappe.log_error(
                    f"Failed to fetch collection: {response.text}",
                    "Postman API Error",
                )
                return

            collection_data = response.json()
            collection_info = collection_data.get("collection", {})

            # Clear all items
            collection_info["item"] = []

            # Update the collection
            update_payload = {"collection": collection_info}
            update_response = requests.put(
                url, headers=headers, json=update_payload, timeout=10
            )

            if update_response.status_code not in [200, 201]:
                frappe.log_error(
                    f"Failed to clear collection: {update_response.text}",
                    "Postman API Error",
                )
            else:
                print("✅ Collection cleared successfully")

        except Exception as e:
            frappe.log_error(
                f"Error clearing collection: {e!s}", "Postman Clear Collection Error"
            )

    def build_postman_item(self, endpoint, doctype_name):
        """Build Postman item data structure"""
        # Handle custom method naming
        if endpoint.get("custom_method"):
            item_name = (
                f"{endpoint['method']} {endpoint.get('method_name', 'Custom Method')}"
            )
        else:
            # Create professional request names based on method and operation
            method = endpoint["method"]
            path = endpoint["path"]

            if method == "GET" and "{{name}}" in path:
                item_name = f"{doctype_name} by ID"
            elif method == "GET" and "{{name}}" not in path:
                item_name = f"List {doctype_name} Records"
            elif method == "POST":
                item_name = f"Create {doctype_name} Record"
            elif method == "PUT":
                item_name = f"Update {doctype_name} Record"
            elif method == "DELETE":
                item_name = f"Delete {doctype_name} Record"
            elif method == "PATCH":
                item_name = f"Patch {doctype_name} Record"
            elif "reportview" in path:
                item_name = f"Advanced {doctype_name} Query"
            else:
                # For other variables, use the variable name
                import re

                variables = re.findall(r"\{\{(\w+)\}\}", path)
                if variables:
                    var_name = variables[0]
                    item_name = f"{doctype_name} by {var_name.title()}"
                else:
                    item_name = f"{method} {doctype_name} Operation"

        # Build request body for POST/PUT requests
        request_body = None
        if endpoint["method"] in ["POST", "PUT", "PATCH"]:
            # Different body structure for custom methods
            if endpoint.get("custom_method"):
                request_body = {
                    "mode": "raw",
                    "raw": json.dumps(
                        {"args": ["arg1", "arg2"], "kwargs": {"key": "value"}}, indent=2
                    ),
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

        # Extract host and port
        host_parts = parsed_url.netloc.split(":")
        host = host_parts[0] if host_parts else "localhost"
        port = host_parts[1] if len(host_parts) > 1 else None

        # Build path array with proper handling of Postman variables
        path_segments = []
        for segment in parsed_url.path.split("/"):
            if segment:  # Skip empty segments
                path_segments.append(segment)

        # Build URL data structure for Postman API
        url_data = {
            "raw": full_url,
            "protocol": parsed_url.scheme or "http",
            "host": [host],
            "path": path_segments,
        }

        # Add port if it exists
        if port:
            url_data["port"] = port

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
            description += (
                f"\n\nCustom Method: {endpoint.get('method_name', 'Unknown')}"
            )
            description += f"\nPath: {endpoint['path']}"
            if endpoint.get("parameters"):
                description += "\n\nParameters:"
                for param in endpoint["parameters"]:
                    description += (
                        f"\n- {param['name']} ({param['type']}): {param['description']}"
                    )

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
            excluded_fieldtypes = [
                "Section Break",
                "Column Break",
                "Tab Break",
                "HTML",
                "Button",
            ]

            # Fields that are system-managed and should not be in request body
            excluded_fieldnames = [
                # Auditable fields
                "creation",
                "modified",
                "modified_by",
                "owner",
                "docstatus",
                "idx",
                "amended_from",
                "creation_date",
                "modified_date",
                # User-specific system fields
                "user",
                "user_type",
                "last_login",
                "login_after",
                "logout_time",
                "last_ip",
                "last_login_ip",
                "api_key",
                "api_secret",
                # Additional system fields
                "read_only",
                "naming_series",
                "parent",
                "parenttype",
                "parentfield",
                "is_system_generated",
                "version",
                "old_parent",
                "lft",
                "rgt",
                "is_group",
                "is_folder",
                "is_home_folder",
                "is_public",
                "is_default",
                "is_active",
                "disabled",
                "enabled",
                "hidden",
                "sort_order",
                "order_by",
                "group_by",
                "color",
                "icon",
                "css_class",
                "custom_css",
                "javascript",
                "workflow_state",
                "workflow_action",
                "workflow_comment",
                "workflow_comment_by",
                "workflow_comment_date",
                "workflow_comment_time",
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
                f"Error generating DocType template for {doctype_name}: {e!s}",
                "DocType Template Error",
            )
            return {
                "doctype": doctype_name,
                "name": "",
                "field1": "",
                "field2": "",
                "field3": "",
            }
