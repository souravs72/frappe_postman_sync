# Copyright (c) 2024, Sourav Singh and contributors
# For license information, please see license.txt

import frappe


def has_app_permission():
    """
    Check if user has permission to access the app
    """
    try:
        # Allow access for all authenticated users
        if frappe.session.user and frappe.session.user != "Guest":
            return True
        return False
    except Exception:
        return False
