# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import json
import time

import frappe


def generate_doctype_apis(doctype_name):
    """Generate APIs for a single DocType and sync to Postman - ULTRA-FAST"""
    try:
        print(f"🚀 Generating APIs for DocType: {doctype_name}")

        # Validate DocType exists
        frappe.get_doc("DocType", doctype_name)

        # Generate CRUD endpoints
        endpoints = [
            {
                "method": "GET",
                "path": f"/api/resource/{doctype_name}",
                "description": f"List {doctype_name} records",
            },
            {
                "method": "POST",
                "path": f"/api/resource/{doctype_name}",
                "description": f"Create {doctype_name} record",
            },
            {
                "method": "GET",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Get {doctype_name} by ID",
            },
            {
                "method": "PUT",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Update {doctype_name} record",
            },
            {
                "method": "DELETE",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Delete {doctype_name} record",
            },
        ]

        # Create API Generator document with endpoints
        api_gen = frappe.new_doc("API Generator")
        api_gen.generation_type = "Single DocType"
        api_gen.doctype_name = doctype_name
        api_gen.auto_generate = False
        api_gen.collection_title = f"{doctype_name} API Collection"
        api_gen.api_endpoints = frappe.as_json(endpoints, indent=2)
        api_gen.status = "Active"
        api_gen.insert()

        # Ultra-fast Postman sync
        api_gen.trigger_postman_sync()

        print(f"✅ Generated APIs for DocType: {doctype_name}")
        return api_gen.name

    except Exception as e:
        print(f"❌ Error generating APIs: {e!s}")
        frappe.log_error(f"Error generating APIs: {e!s}", "API Generation Error")
        raise


def generate_module_apis(module_name):
    """Generate APIs for an entire module and sync to Postman - ULTRA-FAST"""
    try:
        print(f"🚀 Generating APIs for Module: {module_name}")

        # Get all DocTypes in the module
        doctypes = frappe.get_all(
            "DocType",
            filters={
                "module": module_name,
                "custom": 0,
                "name": ["!=", "API Generator"],
            },
            fields=["name"],
        )

        if not doctypes:
            print(f"⚠️ No DocTypes found for module: {module_name}")
            return None

        print(f"📊 Found {len(doctypes)} DocTypes")

        # Cache whitelisted methods ONCE for the entire module
        cached_whitelisted_methods = _get_cached_whitelisted_methods(module_name)

        # Generate ALL endpoints in memory at once
        all_endpoints = _generate_all_endpoints_ultra_fast(
            doctypes, cached_whitelisted_methods
        )

        # Create single API Generator document
        api_gen = frappe.new_doc("API Generator")
        api_gen.generation_type = "Entire Module"
        api_gen.module_name = module_name
        api_gen.auto_generate = False
        api_gen.collection_title = f"{module_name} Module API Collection"
        api_gen.api_endpoints = frappe.as_json(all_endpoints, indent=2)
        api_gen.status = "Active"
        api_gen.description = f"Ultra-fast generation: {len(doctypes)} DocTypes"
        api_gen.insert()

        # Single ultra-fast Postman sync
        api_gen.trigger_postman_sync()

        print(f"✅ Generated APIs for Module: {module_name} ({len(doctypes)} DocTypes)")
        return api_gen.name

    except Exception as e:
        print(f"❌ Error generating APIs: {e!s}")
        frappe.log_error(f"Error generating APIs: {e!s}", "API Generation Error")
        raise


def _get_cached_whitelisted_methods(module_name):
    """Get cached whitelisted methods for a module"""
    cache_key = f"whitelisted_methods_{module_name}"
    cached_methods = frappe.cache().get_value(cache_key)

    if cached_methods is None:
        from frappe_postman_sync.whitelist_scanner import (
            scan_app_for_whitelisted_methods,
        )

        cached_methods = scan_app_for_whitelisted_methods(module_name)
        # Cache for 1 hour
        frappe.cache().set_value(cache_key, cached_methods, expires_in_sec=3600)

    return cached_methods


def _generate_all_endpoints_ultra_fast(doctypes, whitelisted_methods):
    """Generate all endpoints in memory for ultra-fast processing"""
    all_endpoints = {}

    for doctype in doctypes:
        doctype_name = doctype.name

        # Generate CRUD endpoints
        endpoints = [
            {
                "method": "GET",
                "path": f"/api/resource/{doctype_name}",
                "description": f"List {doctype_name} records",
            },
            {
                "method": "POST",
                "path": f"/api/resource/{doctype_name}",
                "description": f"Create {doctype_name} record",
            },
            {
                "method": "GET",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Get {doctype_name} by ID",
            },
            {
                "method": "PUT",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Update {doctype_name} record",
            },
            {
                "method": "DELETE",
                "path": f"/api/resource/{doctype_name}/{{name}}",
                "description": f"Delete {doctype_name} record",
            },
        ]

        # Add whitelisted methods to first DocType only (to avoid duplicates)
        if doctype == doctypes[0] and whitelisted_methods:
            for method in whitelisted_methods:
                endpoints.append(
                    {
                        "method": "POST",
                        "path": f"/api/method/{method['path']}",
                        "description": f"Custom method: {method.get('method_name', 'Unknown')}",
                        "custom_method": True,
                        "method_name": method.get("method_name", "Unknown"),
                    }
                )

        all_endpoints[doctype_name] = endpoints

    return all_endpoints


def clear_postman_collection():
    """Clear all items from Postman collection"""
    try:
        print("🧹 Clearing Postman collection...")
        postman_setting = frappe.get_single("Postman Setting")
        postman_setting.clear_postman_collection()
        print("✅ Postman collection cleared successfully")
        return True
    except Exception as e:
        print(f"❌ Error clearing collection: {e!s}")
        frappe.log_error(f"Error clearing collection: {e!s}", "Clear Collection Error")
        return False


def force_clear_postman_collection():
    """Force clear all items from Postman collection with verification"""
    try:
        print("🧹 Force clearing Postman collection...")
        postman_setting = frappe.get_single("Postman Setting")

        print(f"Collection ID: {postman_setting.collection_id}")
        print(f"Status: {postman_setting.status}")

        # Clear the collection
        postman_setting.clear_postman_collection()

        # Verify it's cleared by checking the collection
        import requests

        api_key = postman_setting.get_password("postman_api_key")
        headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

        url = f"https://api.getpostman.com/collections/{postman_setting.collection_id}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            collection_data = response.json()
            items = collection_data.get("collection", {}).get("item", [])
            print(f"✅ Collection cleared! Current items: {len(items)}")
            if len(items) == 0:
                print("✅ Collection is completely empty")
            else:
                print(f"⚠️ Collection still has {len(items)} items")
        else:
            print(f"❌ Failed to verify collection: {response.status_code}")

        return True
    except Exception as e:
        print(f"❌ Error force clearing collection: {e!s}")
        frappe.log_error(
            f"Error force clearing collection: {e!s}", "Force Clear Collection Error"
        )
        return False


def check_collection_contents():
    """Check what's actually in the Postman collection"""
    try:
        print("🔍 Checking Postman collection contents...")
        postman_setting = frappe.get_single("Postman Setting")

        import requests

        api_key = postman_setting.get_password("postman_api_key")
        headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

        url = f"https://api.getpostman.com/collections/{postman_setting.collection_id}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            collection_data = response.json()
            items = collection_data.get("collection", {}).get("item", [])
            print(f"📊 Current items in collection: {len(items)}")

            if len(items) > 0:
                print("📁 Found folders/items:")
                for i, item in enumerate(items[:10]):  # Show first 10 items
                    print(f"  {i + 1}. {item.get('name', 'Unknown')}")
                    if item.get("item"):  # If it has sub-items
                        sub_items = item.get("item", [])
                        print(f"     └── {len(sub_items)} sub-items")
                        for j, sub_item in enumerate(
                            sub_items[:5]
                        ):  # Show first 5 sub-items
                            print(f"        {j + 1}. {sub_item.get('name', 'Unknown')}")
            else:
                print("✅ Collection is empty")
        else:
            print(f"❌ Failed to fetch collection: {response.status_code}")
            print(f"Response: {response.text}")

        return True
    except Exception as e:
        print(f"❌ Error checking collection: {e!s}")
        frappe.log_error(f"Error checking collection: {e!s}", "Check Collection Error")
        return False
