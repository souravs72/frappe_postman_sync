// Copyright (c) 2024, Sourav Singh and contributors
// For license information, please see license.txt

frappe.ui.form.on("API Generator", {
	refresh: function (frm) {
		if (frm.doc.auto_generate && frm.doc.status === "Active") {
			frm.add_custom_button(
				__("Regenerate APIs"),
				function () {
					frm.call("regenerate_apis").then(() => {
						frm.reload_doc();
					});
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("Test Endpoints"),
				function () {
					frm.call("test_endpoints");
				},
				__("Actions")
			);
		}

		// Add generate button for manual generation
		if (!frm.doc.auto_generate) {
			frm.add_custom_button(
				__("Generate APIs"),
				function () {
					frm.call("generate_api_endpoints").then(() => {
						frm.reload_doc();
					});
				},
				__("Actions")
			);
		}
	},

	generation_type: function (frm) {
		// Show/hide fields based on generation type
		if (frm.doc.generation_type === "Single DocType") {
			frm.set_df_property("doctype_name", "reqd", 1);
			frm.set_df_property("module_name", "reqd", 0);
		} else if (frm.doc.generation_type === "Entire Module") {
			frm.set_df_property("doctype_name", "reqd", 0);
			frm.set_df_property("module_name", "reqd", 1);
		}
	},

	auto_generate: function (frm) {
		if (frm.doc.auto_generate) {
			frm.call("generate_api_endpoints").then(() => {
				frm.reload_doc();
			});
		}
	},
});
