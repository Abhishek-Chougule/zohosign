// Copyright (c) 2023, Abhishek Chougule and contributors
// For license information, please see license.txt

frappe.ui.form.on('Zoho Sign Settings', {
	before_save: function(frm) {
		frm.doc.site_url=window.location.origin;
	}
});
