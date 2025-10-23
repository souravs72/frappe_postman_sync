// Copyright (c) 2024, Sourav Singh and contributors
// For license information, please see license.txt

frappe.ui.form.on("Postman Setting", {
	refresh: function (frm) {
		// Add action buttons
		frm.add_custom_button(
			__("Sync to Postman"),
			function () {
				frm.call("sync_to_postman").then(() => {
					frm.reload_doc();
				});
			},
			__("Actions"),
		);

		frm.add_custom_button(
			__("Test Connection"),
			function () {
				frm.call("validate_postman_connection").then(() => {
					frm.reload_doc();
				});
			},
			__("Actions"),
		);

		frm.add_custom_button(
			__("Scan Whitelisted Methods"),
			function () {
				frappe.call({
					method: "frappe_postman_sync.api.help.scan_and_sync_whitelisted_methods",
					callback: function (r) {
						if (r.message) {
							frappe.msgprint(
								r.message.message || "Whitelisted methods scanned successfully!",
							);
							frm.reload_doc();
						}
					},
				});
			},
			__("Actions"),
		);

		frm.add_custom_button(
			__("System Status"),
			function () {
				frappe.call({
					method: "frappe_postman_sync.api.help.get_system_status",
					callback: function (r) {
						if (r.message) {
							let status = r.message;
							let message = `
								<h4>System Status</h4>
								<p><strong>Custom DocTypes:</strong> ${status.total_custom_doctypes}</p>
								<p><strong>API Generators:</strong> ${status.total_api_generators} (${
									status.active_api_generators
								} active)</p>
								<p><strong>Whitelisted Methods:</strong> ${status.total_whitelisted_methods}</p>
								<p><strong>Postman Configured:</strong> ${status.postman_configured ? "Yes" : "No"}</p>
								<p><strong>Auto Sync:</strong> ${status.auto_sync_enabled ? "Enabled" : "Disabled"}</p>
								${status.last_sync ? `<p><strong>Last Sync:</strong> ${status.last_sync}</p>` : ""}
							`;
							frappe.msgprint({
								title: "System Status",
								message: message,
								indicator: status.postman_configured ? "green" : "orange",
							});
						}
					},
				});
			},
			__("Actions"),
		);
	},

	enable_auto_sync: function (frm) {
		if (frm.doc.enable_auto_sync) {
			frm.call("validate_postman_connection").then(() => {
				frm.reload_doc();
			});
		}
	},
});
