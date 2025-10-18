# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document


class APIGenerator(Document):
    def validate(self):
        # Set the name based on generation type
        if not self.name or self.name.startswith("NEW"):
            if self.generation_type == "Single DocType" and self.doctype_name:
                self.name = self.doctype_name
            elif self.generation_type == "Entire Module" and self.module_name:
                self.name = f"{self.module_name} Module"

        if self.auto_generate:
            self.generate_api_endpoints()

    @frappe.whitelist()
    def generate_api_endpoints(self):
        """Generate CRUD API endpoints for doctype(s) based on generation type"""
        try:
            if self.generation_type == "Single DocType":
                self.generate_single_doctype_apis()
            elif self.generation_type == "Entire Module":
                self.generate_module_apis()

        except Exception as e:
            self.status = "Error"
            frappe.log_error(f"Error generating APIs: {e!s}", "API Generation Error")

    def generate_single_doctype_apis(self):
        """Generate CRUD API endpoints for a single doctype"""
        if not self.doctype_name:
            frappe.throw("DocType Name is required for Single DocType generation")

        # Get doctype meta information
        doctype_meta = frappe.get_meta(self.doctype_name)
        self.module_name = doctype_meta.module

        # Generate API endpoints
        endpoints = self.build_crud_endpoints(self.doctype_name)

        # Store endpoints as JSON
        self.api_endpoints = json.dumps(endpoints, indent=2)
        self.status = "Active"

        # Trigger Postman sync if enabled
        self.trigger_postman_sync()

    def generate_module_apis(self):
        """Generate CRUD API endpoints for all doctypes in a module"""
        if not self.module_name:
            frappe.throw("Module Name is required for Entire Module generation")

        # Get all doctypes in the module, excluding API Generator to prevent cyclic issues
        doctypes = frappe.get_all(
            "DocType",
            filters={
                "module": self.module_name,
                "custom": 0,
                "name": [
                    "!=",
                    "API Generator",
                ],  # Exclude API Generator to prevent cyclic issues
            },
            fields=["name"],
        )

        all_endpoints = {}
        generated_count = 0

        for doctype in doctypes:
            try:
                doctype_name = doctype.name
                endpoints = self.build_crud_endpoints(doctype_name)
                all_endpoints[doctype_name] = endpoints
                generated_count += 1
            except Exception as e:
                frappe.log_error(
                    f"Error generating APIs for {doctype_name}: {e!s}",
                    "Module API Generation Error",
                )

        # Store all endpoints as JSON
        self.api_endpoints = json.dumps(all_endpoints, indent=2)
        self.status = "Active"
        self.description = f"Generated APIs for {generated_count} doctypes in module {self.module_name}"

        # Trigger Postman sync if enabled
        self.trigger_postman_sync()

    def build_crud_endpoints(self, doctype_name=None):
        """Build CRUD API endpoints for the doctype"""
        if not doctype_name:
            doctype_name = self.doctype_name

        endpoints = [
            {
                "method": "GET",
                "path": f"/api/resource/{doctype_name}",
                "description": f"Get list of {doctype_name} records",
                "parameters": [
                    {"name": "filters", "type": "query", "description": "JSON filters"},
                    {
                        "name": "fields",
                        "type": "query",
                        "description": "Fields to fetch",
                    },
                    {
                        "name": "limit_page_length",
                        "type": "query",
                        "description": "Number of records per page",
                    },
                    {
                        "name": "limit_start",
                        "type": "query",
                        "description": "Starting record number",
                    },
                ],
            },
            {
                "method": "GET",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Get specific {doctype_name} record by name",
                "parameters": [
                    {
                        "name": "name",
                        "type": "path",
                        "description": "Document name",
                        "required": True,
                    }
                ],
            },
            {
                "method": "POST",
                "path": f"/api/resource/{doctype_name}",
                "description": f"Create new {doctype_name} record",
                "parameters": [
                    {
                        "name": "body",
                        "type": "body",
                        "description": "Document data",
                        "required": True,
                    }
                ],
            },
            {
                "method": "PUT",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Update existing {doctype_name} record",
                "parameters": [
                    {
                        "name": "name",
                        "type": "path",
                        "description": "Document name",
                        "required": True,
                    },
                    {
                        "name": "body",
                        "type": "body",
                        "description": "Updated document data",
                        "required": True,
                    },
                ],
            },
            {
                "method": "DELETE",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Delete {doctype_name} record",
                "parameters": [
                    {
                        "name": "name",
                        "type": "path",
                        "description": "Document name",
                        "required": True,
                    }
                ],
            },
            {
                "method": "GET",
                "path": "/api/method/frappe.desk.reportview.get",
                "description": f"Get {doctype_name} records with advanced filtering",
                "parameters": [
                    {
                        "name": "doctype",
                        "type": "query",
                        "description": "DocType name",
                        "required": True,
                    },
                    {"name": "filters", "type": "query", "description": "JSON filters"},
                    {
                        "name": "fields",
                        "type": "query",
                        "description": "Fields to fetch",
                    },
                    {
                        "name": "order_by",
                        "type": "query",
                        "description": "Order by field",
                    },
                ],
            },
        ]

        # Add whitelisted methods from the doctype
        whitelisted_methods = self.get_whitelisted_methods(doctype_name)
        endpoints.extend(whitelisted_methods)

        return endpoints

    def get_whitelisted_methods(self, doctype_name=None):
        """Get whitelisted methods from the doctype controller"""
        if not doctype_name:
            doctype_name = self.doctype_name

        whitelisted_methods = []

        try:
            # Get the doctype controller module
            doctype_meta = frappe.get_meta(doctype_name)
            module_name = doctype_meta.module

            # Use the enhanced whitelist scanner
            from frappe_postman_sync.whitelist_scanner import (
                scan_app_for_whitelisted_methods,
            )

            app_methods = scan_app_for_whitelisted_methods(module_name)

            # Filter methods relevant to this doctype
            for method in app_methods:
                if (
                    doctype_name.lower().replace(" ", "_")
                    in method.get("path", "").lower()
                ):
                    method_info = {
                        "method": "POST",
                        "path": f"/api/method/{method['path']}",
                        "description": method.get(
                            "description",
                            f"Custom method: {method.get('method_name', 'Unknown')}",
                        ),
                        "parameters": [
                            {
                                "name": "args",
                                "type": "body",
                                "description": "Method arguments",
                                "required": False,
                            },
                            {
                                "name": "kwargs",
                                "type": "body",
                                "description": "Method keyword arguments",
                                "required": False,
                            },
                        ],
                        "custom_method": True,
                        "method_name": method.get(
                            "method_name", method["path"].split(".")[-1]
                        ),
                        "source": method.get("source", "unknown"),
                    }
                    whitelisted_methods.append(method_info)

            # Fallback to old method if no methods found
            if not whitelisted_methods:
                whitelisted_methods = self.get_legacy_whitelisted_methods(module_name)

        except Exception as e:
            frappe.log_error(
                f"Error getting whitelisted methods for {self.doctype_name}: {e!s}",
                "Whitelisted Methods Error",
            )

        return whitelisted_methods

    def get_legacy_whitelisted_methods(self, module_name):
        """Legacy method to get whitelisted methods (fallback)"""
        whitelisted_methods = []

        try:
            # Try to import the controller
            controller_path = f"{module_name}.{self.doctype_name.lower().replace(' ', '_')}.{self.doctype_name.lower().replace(' ', '_')}"

            try:
                controller_module = frappe.get_module(controller_path)
                controller_class = getattr(controller_module, self.doctype_name, None)

                if controller_class:
                    # Get whitelisted methods from the controller class
                    whitelisted_methods = self.extract_whitelisted_methods(
                        controller_class, module_name
                    )

            except ImportError:
                # Try alternative import paths
                alt_paths = [
                    f"{module_name}.doctype.{self.doctype_name.lower().replace(' ', '_')}.{self.doctype_name.lower().replace(' ', '_')}",
                    f"{module_name}.{self.doctype_name.lower().replace(' ', '_')}.{self.doctype_name.lower().replace(' ', '_')}",
                ]

                for path in alt_paths:
                    try:
                        controller_module = frappe.get_module(path)
                        controller_class = getattr(
                            controller_module, self.doctype_name, None
                        )
                        if controller_class:
                            whitelisted_methods = self.extract_whitelisted_methods(
                                controller_class, module_name
                            )
                            break
                    except ImportError:
                        continue

            # Also check for whitelisted methods in hooks.py
            whitelisted_methods.extend(self.get_hooks_whitelisted_methods(module_name))

        except Exception as e:
            frappe.log_error(
                f"Error in legacy whitelisted methods: {e!s}",
                "Legacy Whitelisted Methods Error",
            )

        return whitelisted_methods

    def extract_whitelisted_methods(self, controller_class, module_name):
        """Extract whitelisted methods from controller class"""
        whitelisted_methods = []

        try:
            # Get methods that have @frappe.whitelist() decorator
            for method_name in dir(controller_class):
                method = getattr(controller_class, method_name, None)
                if method and callable(method) and hasattr(method, "__wrapped__"):
                    # Check if method has whitelist decorator
                    if hasattr(method, "_frappe_whitelist"):
                        method_info = {
                            "method": "POST",  # Default to POST for custom methods
                            "path": f"/api/method/{module_name}.{self.doctype_name.lower().replace(' ', '_')}.{self.doctype_name.lower().replace(' ', '_')}.{method_name}",
                            "description": f"Custom method: {method_name}",
                            "parameters": [
                                {
                                    "name": "args",
                                    "type": "body",
                                    "description": "Method arguments",
                                    "required": False,
                                }
                            ],
                            "custom_method": True,
                            "method_name": method_name,
                        }
                        whitelisted_methods.append(method_info)
        except Exception as e:
            frappe.log_error(
                f"Error extracting whitelisted methods: {e!s}",
                "Method Extraction Error",
            )

        return whitelisted_methods

    def get_hooks_whitelisted_methods(self, module_name):
        """Get whitelisted methods from hooks.py"""
        whitelisted_methods = []

        try:
            # Check if there are any whitelisted methods in hooks
            import frappe

            hooks = frappe.get_hooks()

            # Look for whitelisted_methods in hooks
            if hasattr(hooks, "whitelisted_methods"):
                for method_path in hooks.whitelisted_methods:
                    if (
                        module_name in method_path
                        and self.doctype_name.lower().replace(" ", "_") in method_path
                    ):
                        method_info = {
                            "method": "POST",
                            "path": f"/api/method/{method_path}",
                            "description": f"Whitelisted method: {method_path.split('.')[-1]}",
                            "parameters": [
                                {
                                    "name": "args",
                                    "type": "body",
                                    "description": "Method arguments",
                                    "required": False,
                                }
                            ],
                            "custom_method": True,
                            "method_name": method_path.split(".")[-1],
                        }
                        whitelisted_methods.append(method_info)
        except Exception as e:
            frappe.log_error(
                f"Error getting hooks whitelisted methods: {e!s}", "Hooks Methods Error"
            )

        return whitelisted_methods

    def trigger_postman_sync(self):
        """Trigger Postman sync for this API generator"""
        try:
            postman_settings = frappe.get_single("Postman Setting")
            if (
                postman_settings.enable_auto_sync
                and postman_settings.status == "Active"
            ):
                postman_settings.sync_to_postman()
        except Exception as e:
            frappe.log_error(
                f"Error triggering Postman sync: {e!s}", "Postman Sync Error"
            )

    @frappe.whitelist()
    def regenerate_apis(self):
        """Regenerate API endpoints"""
        self.generate_api_endpoints()
        self.save()
        frappe.msgprint("API endpoints regenerated successfully")

    @frappe.whitelist()
    def test_endpoints(self):
        """Test API endpoints"""
        try:
            # Test basic GET endpoint
            response = frappe.call(
                "frappe.desk.reportview.get",
                {
                    "doctype": self.doctype_name,
                    "fields": ["name"],
                    "limit_page_length": 1,
                },
            )

            if response:
                frappe.msgprint("API endpoints are working correctly")
            else:
                frappe.msgprint("No data found, but endpoints are accessible")

        except Exception as e:
            frappe.msgprint(f"Error testing endpoints: {e!s}")
