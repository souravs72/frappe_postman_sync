app_name = "frappe_postman_sync"
app_title = "Frappe Postman Sync"
app_publisher = "Sourav Singh"
app_description = "A developer utility app that automatically generates and syncs REST API endpoints from your Frappe site to Postman."
app_email = "souravsingh2609@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "frappe_postman_sync",
# 		"logo": "/assets/frappe_postman_sync/logo.png",
# 		"title": "Frappe Postman Sync",
# 		"route": "/frappe_postman_sync",
# 		"has_permission": "frappe_postman_sync.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/frappe_postman_sync/css/frappe_postman_sync.css"
# app_include_js = "/assets/frappe_postman_sync/js/frappe_postman_sync.js"

# include js, css files in header of web template
# web_include_css = "/assets/frappe_postman_sync/css/frappe_postman_sync.css"
# web_include_js = "/assets/frappe_postman_sync/js/frappe_postman_sync.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_postman_sync/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Postman Settings": "frappe_postman_sync/doctype/postman_settings/postman_settings.js",
	"API Generator": "frappe_postman_sync/doctype/api_generator/api_generator.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "frappe_postman_sync/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "frappe_postman_sync.utils.jinja_methods",
# 	"filters": "frappe_postman_sync.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_postman_sync.install.before_install"
after_install = "frappe_postman_sync.services.sync_existing_doctypes"

# Uninstallation
# ------------

# before_uninstall = "frappe_postman_sync.uninstall.before_uninstall"
# after_uninstall = "frappe_postman_sync.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "frappe_postman_sync.utils.before_app_install"
# after_app_install = "frappe_postman_sync.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "frappe_postman_sync.utils.before_app_uninstall"
# after_app_uninstall = "frappe_postman_sync.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_postman_sync.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"DocType": {
		"after_insert": "frappe_postman_sync.services.auto_generate_api_for_doctype",
		"on_update": "frappe_postman_sync.services.auto_generate_api_for_doctype",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"frappe_postman_sync.tasks.all"
# 	],
# 	"daily": [
# 		"frappe_postman_sync.tasks.daily"
# 	],
# 	"hourly": [
# 		"frappe_postman_sync.tasks.hourly"
# 	],
# 	"weekly": [
# 		"frappe_postman_sync.tasks.weekly"
# 	],
# 	"monthly": [
# 		"frappe_postman_sync.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "frappe_postman_sync.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "frappe_postman_sync.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "frappe_postman_sync.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_postman_sync.utils.before_request"]
# after_request = ["frappe_postman_sync.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_postman_sync.utils.before_job"]
# after_job = ["frappe_postman_sync.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"frappe_postman_sync.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
