// Copyright (c) 2023, Abhishek Chougule and contributors
// For license information, please see license.txt

frappe.ui.form.on('Zoho Sign Contracts', {
    before_save:function(frm){
        
        var userEmail = frm.doc.created_by;
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'User',
                filters: { 'email': userEmail },
                fieldname: ['name', 'full_name']
            },
            callback: function(response) {
                var userDoc = response.message;

                if (userDoc) {
                    var userName = userDoc.full_name;
                    let fullnm=frm.doc.c_first_name+' '+frm.doc.c_last_name
                    if(frm.doc.created_by)
                    {
                    frm.doc.recipient_emails=frm.doc.lead_email+','+frm.doc.created_by
                    frm.doc.recipient_names=fullnm+','+userName
                    }
                    else
                    {
                        frm.doc.recipient_emails=frm.doc.lead_email
                        frm.doc.recipient_names=fullnm
                    }
                } else {
                    console.log('User not found');
                }
            }
        });
        
    },
    
	refresh: function(frm) {
        // frm.add_custom_button(__("Get Signed Document"), function () {
        //     frappe.call({
        //         method: '',
        //         doc:frm.doc,
        //         args: {
        //             'r_id': frm.doc.note
        //         },
        //         callback: function (r) {}
        //     });
        // });
		if (frm.doc.attach_contract,frm.doc.recipient_names,frm.doc.recipient_emails) {
            frm.add_custom_button(__("Send for Signature"), function () {
                frappe.call({
                    method: 'zohosign.api.get_zoho_sign_credentials',
                    callback: function (r) {
                        if (r.message) {
                            const { client_id, refresh_token, client_secret } = r.message;
							
                            frappe.call({
                                method: 'zohosign.api.docsign',
                                args: {
                                    'client_id': client_id,
                                    'refresh_token': refresh_token,
                                    'client_secret': client_secret,
                                    'file_url': frm.doc.attach_contract,
                                    'request_name': frm.doc.name,
                                    'recipient_names': frm.doc.recipient_names, 
                                    'recipient_emails': frm.doc.recipient_emails
                                },
                                callback: function (response) {},
                            });
                        }
                    },
                });
            });
        }
	}
});