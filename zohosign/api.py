# Copyright (c) 2022, Abhishek Chougule, OneHash Inc and contributors
# For license information, please see license.txt

import requests
import frappe
from io import BytesIO
import json
import re

# https://{url}/api/method/zohosign.api.get_sign_webhook

# data = json.loads(raw_data.decode('utf-8'))
# r_id = data["requests"]["request_id"]
# r_name = data["requests"]["request_name"]

zoho_sign_settings = frappe.get_single("Zoho Sign Settings")
site_url=str(zoho_sign_settings.site_url)
z_access_token=str(zoho_sign_settings.access_token)

@frappe.whitelist()
def get_zoho_sign_credentials():
    zoho_sign_settings = frappe.get_single("Zoho Sign Settings")
    
    return {
        'client_id': zoho_sign_settings.client_id,
        'refresh_token': zoho_sign_settings.refresh_token,
        'client_secret': zoho_sign_settings.client_secret,
    }

# @frappe.whitelist()
# def get_signed_doc(r_id):
#      url = "https://sign.zoho.com/api/v1/requests/"+str(r_id)+"/pdf"

#     payload = {}
#     headers = {
#     'Authorization': 'Zoho-oauthtoken '+str(z_access_token),
#     'Cookie': 'JSESSIONID=A221662ED0807CBBB998DDF83A0C55B7; _zcsr_tmp=b1ed60e9-39f1-4495-b069-8db74a9072d7; c61ac045a3=6b9cee97758e3400a29d7e000f9fb33f; zscsrfcookie=b1ed60e9-39f1-4495-b069-8db74a9072d7'
#     }

#     response = requests.request("GET", url, headers=headers, data=payload)

@frappe.whitelist(allow_guest=True)
def get_sign_webhook():
    try:
        raw_data = frappe.request.get_data()
        data = f'''{raw_data}'''
        pattern = r'"request_name"\s*:\s*"?([^"]*)"?[^}]*?"request_id"\s*:\s*"?(\d+)"?'
        match = re.search(pattern, data)

        if match:
            r_name = match.group(1)
            r_id = match.group(2)

        if raw_data:       
            # contr= frappe.get_doc('Zoho Sign Contracts',str(r_name))
            # contr.note=str(r_id)
            # contr.save(ignore_permissions = True)

            # tmp=r_name.split('-')
            # r_name=str(tmp[0])
            # z_access_token=str(tmp[1])
            
            url = "https://sign.zoho.com/api/v1/requests/"+str(r_id)+"/pdf"

            payload = {}
            headers = {
            'Authorization': 'Zoho-oauthtoken '+str(z_access_token),
            'Cookie': 'JSESSIONID=A221662ED0807CBBB998DDF83A0C55B7; _zcsr_tmp=b1ed60e9-39f1-4495-b069-8db74a9072d7; c61ac045a3=6b9cee97758e3400a29d7e000f9fb33f; zscsrfcookie=b1ed60e9-39f1-4495-b069-8db74a9072d7'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            # cont = frappe.get_doc({
            #     'doctype':'Zoho Sign Contracts',
            #     'note': str(response.status_code)
                
            #     })
            # cont.insert(ignore_permissions = True)
            
            if response.status_code == 200: 
                if len(response.content) == 0:
                    cont = frappe.get_doc({
                    'doctype':'Zoho Sign Contracts',
                    'note':'Attachment File is Empty for : '+str(r_name)
                    
                    })
                    cont.insert(ignore_permissions = True)

                else:
                    # cont = frappe.get_doc({
                    # 'doctype':'Zoho Sign Contracts',
                    # 'note':'Attachment File is Full for : '+str(r_name)
                    
                    # })
                    # cont.insert(ignore_permissions = True)
                    with open(site_url[8:]+"/public/files/"+str(r_name)+".pdf", "wb") as pdf_file:
                        pdf_file.write(response.content)
                        contr= frappe.get_doc('Zoho Sign Contracts',str(r_name))
                        contr.signed_attachment=str(site_url)+'/files/'+str(r_name)+'.pdf'
                        contr.status="Signed"
                        contr.save(ignore_permissions = True)
  
            else:
                cont = frappe.get_doc({
                'doctype':'Zoho Sign Contracts',
                'note': 'Failed to retrieve PDF. Status Code '+str(response.status_code)+' , Res: '+str(response.text)
                
                })
                cont.insert(ignore_permissions = True)
            
        
    except Exception as e:
        frappe.log_error(e,'e')


@frappe.whitelist()
def emailforsign(request_id,access_token):
    url = "https://sign.zoho.com/api/v1/requests/"+str(request_id)+"/submit"
    payload = {}
    headers = {
    'Authorization': 'Zoho-oauthtoken '+str(access_token),
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'JSESSIONID=8761E71024022FF5D12B2BBAAED1D64A; _zcsr_tmp=b1ed60e9-39f1-4495-b069-8db74a9072d7; c61ac045a3=6b9cee97758e3400a29d7e000f9fb33f; zscsrfcookie=b1ed60e9-39f1-4495-b069-8db74a9072d7'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # frappe.msgprint(str(response.text))



@frappe.whitelist()
def docsign(refresh_token,client_id,client_secret,request_name,recipient_names,recipient_emails,file_url):
    recipient_names=recipient_names.split(',')
    recipient_emails=recipient_emails.split(',')

    url = "https://accounts.zoho.com/oauth/v2/token?refresh_token="+str(refresh_token)+"&client_id="+str(client_id)+"&client_secret="+str(client_secret)+"&redirect_uri=https%3A%2F%2Fsign.zoho.com&grant_type=refresh_token"
    payload = {}
    headers = {
    'Cookie': '6e73717622=94da0c17b67b4320ada519c299270f95; _zcsr_tmp=4603abf6-5a85-4b00-9d97-84eec8af0da7; iamcsr=4603abf6-5a85-4b00-9d97-84eec8af0da7'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    json_response = response.json()
    access_token = str(json_response['access_token'])

    zoho_sign_settings = frappe.get_single("Zoho Sign Settings")
    zoho_sign_settings.access_token=str(access_token)
    zoho_sign_settings.save(ignore_permissions=True)

    url = "https://sign.zoho.com/api/v1/requests"
    file_response = requests.get(file_url)
    file_content = BytesIO(file_response.content)

    actions = []

    for i, (name, email) in enumerate(zip(recipient_names, recipient_emails)):
        action = {
            "recipient_name": str(name),
            "recipient_email": str(email),
            "action_type": "SIGN",
            "private_notes": "Please get back to us for further queries",
            "signing_order": i,
            "verify_recipient": False,
        }
        actions.append(action)

    payload = {
    'data': json.dumps({
        "requests": {
            "request_name": str(request_name),
            "actions": actions,
            "expiration_days": 1,
            "is_sequential": True,
            "email_reminders": True,
            "reminder_period": 8
        }
    })
}

    files = [
        ('file', ('NDA.pdf', file_content, 'application/pdf'))
    ]
    headers = {
        'Authorization': 'Zoho-oauthtoken '+str(access_token)
    }
    response = requests.post(url, headers=headers, data=payload, files=files)
    json_response = response.json()
    frappe.msgprint('Document Sent for Signature !')
 
    request_id = str(json_response['requests']['request_id'])

    emailforsign(request_id,access_token)
