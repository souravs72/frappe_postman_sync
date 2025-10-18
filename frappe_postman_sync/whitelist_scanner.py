# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import json
import os

import frappe


def scan_all_whitelisted_methods():
    """
    Scan all apps for whitelisted methods and return them
    """
    all_whitelisted_methods = {}

    try:
        # Get all installed apps
        installed_apps = frappe.get_installed_apps()

        for app in installed_apps:
            if app == "frappe":
                continue  # Skip core frappe app

            app_whitelisted_methods = scan_app_for_whitelisted_methods(app)
            if app_whitelisted_methods:
                all_whitelisted_methods[app] = app_whitelisted_methods

    except Exception as e:
        frappe.log_error(
            f"Error scanning whitelisted methods: {e!s}", "Whitelist Scanner Error"
        )

    return all_whitelisted_methods


def scan_app_for_whitelisted_methods(app_name):
    """
    Scan a specific app for whitelisted methods
    """
    whitelisted_methods = []

    try:
        app_path = frappe.get_app_path(app_name)

        # Scan hooks.py for whitelisted_methods
        hooks_methods = scan_hooks_for_whitelisted_methods(app_path)
        whitelisted_methods.extend(hooks_methods)

        # Scan doctype controllers
        doctype_methods = scan_doctype_controllers(app_path, app_name)
        whitelisted_methods.extend(doctype_methods)

        # Scan other Python files for @frappe.whitelist decorators
        file_methods = scan_python_files_for_whitelisted_methods(app_path, app_name)
        whitelisted_methods.extend(file_methods)

    except Exception as e:
        frappe.log_error(
            f"Error scanning app {app_name} for whitelisted methods: {e!s}",
            "App Scanner Error",
        )

    return whitelisted_methods


def scan_hooks_for_whitelisted_methods(app_path):
    """
    Scan hooks.py file for whitelisted_methods
    """
    whitelisted_methods = []

    try:
        hooks_file = os.path.join(app_path, "hooks.py")
        if not os.path.exists(hooks_file):
            return whitelisted_methods

        with open(hooks_file) as f:
            content = f.read()

        # Parse the hooks.py file to find whitelisted_methods
        lines = content.split("\n")
        in_whitelisted_methods = False

        for line in lines:
            line = line.strip()

            if "whitelisted_methods" in line and "=" in line:
                in_whitelisted_methods = True
                continue

            if in_whitelisted_methods:
                if line.startswith("]") or line.startswith("}"):
                    break
                if "[" in line and "]" in line:
                    # Single line list
                    method_line = line.split("[")[1].split("]")[0]
                    methods = [m.strip().strip("\"'") for m in method_line.split(",")]
                    for method in methods:
                        if method and "." in method:
                            whitelisted_methods.append(
                                {
                                    "path": method,
                                    "source": "hooks.py",
                                    "description": f"Whitelisted method from hooks: {method.split('.')[-1]}",
                                }
                            )
                    break
                elif '"' in line or "'" in line:
                    # Multi-line list item
                    method = line.strip().strip(",").strip("\"'")
                    if method and "." in method:
                        whitelisted_methods.append(
                            {
                                "path": method,
                                "source": "hooks.py",
                                "description": f"Whitelisted method from hooks: {method.split('.')[-1]}",
                            }
                        )

    except Exception as e:
        frappe.log_error(f"Error scanning hooks.py: {e!s}", "Hooks Scanner Error")

    return whitelisted_methods


def scan_doctype_controllers(app_path, app_name):
    """
    Scan doctype controllers for whitelisted methods
    """
    whitelisted_methods = []

    try:
        doctype_path = os.path.join(app_path, app_name, "doctype")
        if not os.path.exists(doctype_path):
            return whitelisted_methods

        for doctype_dir in os.listdir(doctype_path):
            doctype_py_file = os.path.join(
                doctype_path, doctype_dir, f"{doctype_dir}.py"
            )
            if os.path.exists(doctype_py_file):
                methods = scan_file_for_whitelisted_methods(
                    doctype_py_file, app_name, doctype_dir
                )
                whitelisted_methods.extend(methods)

    except Exception as e:
        frappe.log_error(
            f"Error scanning doctype controllers: {e!s}", "DocType Scanner Error"
        )

    return whitelisted_methods


def scan_python_files_for_whitelisted_methods(app_path, app_name):
    """
    Scan Python files for @frappe.whitelist decorators
    """
    whitelisted_methods = []

    try:
        for root, dirs, files in os.walk(app_path):
            # Skip certain directories
            dirs[:] = [
                d for d in dirs if d not in ["__pycache__", ".git", "node_modules"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, app_path)

                    methods = scan_file_for_whitelisted_methods(
                        file_path, app_name, relative_path
                    )
                    whitelisted_methods.extend(methods)

    except Exception as e:
        frappe.log_error(
            f"Error scanning Python files: {e!s}", "Python Files Scanner Error"
        )

    return whitelisted_methods


def scan_file_for_whitelisted_methods(file_path, app_name, context=""):
    """
    Scan a single Python file for @frappe.whitelist decorators
    """
    whitelisted_methods = []

    try:
        with open(file_path) as f:
            content = f.read()

        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "@frappe.whitelist" in line or "@whitelist" in line:
                # Find the function definition on the next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    func_line = lines[j].strip()
                    if func_line.startswith("def "):
                        func_name = func_line.split("def ")[1].split("(")[0]

                        # Determine the module path
                        module_path = determine_module_path(
                            file_path, app_name, func_name
                        )

                        whitelisted_methods.append(
                            {
                                "path": module_path,
                                "source": context,
                                "description": f"Whitelisted method: {func_name}",
                                "method_name": func_name,
                                "file_path": file_path,
                            }
                        )
                        break

    except Exception as e:
        frappe.log_error(
            f"Error scanning file {file_path}: {e!s}", "File Scanner Error"
        )

    return whitelisted_methods


def determine_module_path(file_path, app_name, func_name):
    """
    Determine the module path for a whitelisted method
    """
    try:
        # Convert file path to module path
        relative_path = os.path.relpath(file_path, frappe.get_app_path(app_name))
        module_path = relative_path.replace("/", ".").replace(".py", "")

        # Remove __init__.py from path
        module_path = module_path.replace(".__init__", "")

        # Ensure it starts with app name
        if not module_path.startswith(app_name):
            module_path = f"{app_name}.{module_path}"

        return f"{module_path}.{func_name}"

    except Exception as e:
        frappe.log_error(f"Error determining module path: {e!s}", "Module Path Error")
        return f"{app_name}.unknown.{func_name}"


@frappe.whitelist()
def get_all_whitelisted_methods():
    """
    Get all whitelisted methods across all apps
    """
    return scan_all_whitelisted_methods()


@frappe.whitelist()
def get_app_whitelisted_methods(app_name):
    """
    Get whitelisted methods for a specific app
    """
    return scan_app_for_whitelisted_methods(app_name)


@frappe.whitelist()
def sync_whitelisted_methods_to_postman():
    """
    Sync all discovered whitelisted methods to Postman
    """
    try:
        all_methods = scan_all_whitelisted_methods()

        # Create API Generator entries for discovered methods
        for app_name, methods in all_methods.items():
            for method in methods:
                # Create a generic API Generator for whitelisted methods
                create_whitelisted_method_api_generator(method, app_name)

        return {
            "status": "success",
            "message": f"Found and synced {len(all_methods)} whitelisted methods",
        }

    except Exception as e:
        frappe.log_error(
            f"Error syncing whitelisted methods: {e!s}", "Whitelist Sync Error"
        )
        return {"status": "error", "message": str(e)}


def create_whitelisted_method_api_generator(method, app_name):
    """
    Create API Generator entry for a whitelisted method
    """
    try:
        # Check if API Generator already exists
        existing = frappe.db.exists("API Generator", method["path"])
        if existing:
            return

        # Create API Generator for whitelisted method
        api_gen = frappe.get_doc(
            {
                "doctype": "API Generator",
                "doctype_name": method["path"],
                "auto_generate": 1,
                "created_by_doctype": 0,
                "status": "Active",
                "description": method.get(
                    "description",
                    f"Whitelisted method from {method.get('source', 'unknown')}",
                ),
            }
        )

        # Generate API endpoints for the whitelisted method
        endpoints = [
            {
                "method": "POST",
                "path": f"/api/method/{method['path']}",
                "description": method.get("description", "Whitelisted method"),
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
                "method_name": method.get("method_name", method["path"].split(".")[-1]),
                "source": method.get("source", "unknown"),
            }
        ]

        api_gen.api_endpoints = json.dumps(endpoints, indent=2)
        api_gen.insert(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(
            f"Error creating API Generator for whitelisted method: {e!s}",
            "API Generator Creation Error",
        )
