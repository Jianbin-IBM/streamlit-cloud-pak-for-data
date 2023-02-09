import requests
import base64,json
from urllib3.exceptions import InsecureRequestWarning

# apikey='mPhmEnNRY4MAKwCjtKNItdFo2NgbVwiJhb8GjZhub5Yy'
# auth_ok, headers, error_msg = cpd_helpers.authenticate(apikey)

# print(headers)

'''
curl -k -X GET ‘https://cpd-cpd-instance.anz-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud/v2/projects’ -H ‘Accept: application/json’ -H ‘Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Iks4U0dvLU14Si02US0yNDRqTldZV1dpeEZORVdxNkd4VEpnenNELW9YYzAifQ.eyJ1c2VybmFtZSI6ImpidGFuZyIsInJvbGUiOiJBZG1pbiIsInBlcm1pc3Npb25zIjpbInNpZ25faW5fb25seSIsImNyZWF0ZV9wcm9qZWN0IiwiY3JlYXRlX3NwYWNlIiwiYWNjZXNzX2FkdmFuY2VkX21hcHBpbmdfY2FwYWJpbGl0aWVzIiwiYWNjZXNzX2NhdGFsb2ciLCJhY2Nlc3NfZGF0YV9xdWFsaXR5X2Fzc2V0X3R5cGVzIiwidmlld19nb3Zlcm5hbmNlX2FydGlmYWN0cyIsImF1dGhvcl9nb3Zlcm5hbmNlX2FydGlmYWN0cyIsIm1hbmFnZV9nbG9zc2FyeSIsIm1hbmFnZV9jYXRlZ29yaWVzIiwibWFuYWdlX2dvdmVybmFuY2Vfd29ya2Zsb3ciLCJtb25pdG9yX3NwYWNlIiwibW9uaXRvcl9wcm9qZWN0Iiwidmlld19wbGF0Zm9ybV9oZWFsdGgiLCJhZG1pbmlzdHJhdG9yIiwiY2FuX3Byb3Zpc2lvbiIsIm1hbmFnZV92YXVsdHNfYW5kX3NlY3JldHMiLCJzaGFyZV9zZWNyZXRzIiwiYWRkX3ZhdWx0cyIsIm1hbmFnZV9jYXRhbG9nIl0sImdyb3VwcyI6WzEwMDA2LDEwMDA3LDEwMDAwXSwic3ViIjoiamJ0YW5nIiwiaXNzIjoiS05PWFNTTyIsImF1ZCI6IkRTWCIsInVpZCI6IjEwMDAzMzEwMjAiLCJhdXRoZW50aWNhdG9yIjoiZGVmYXVsdCIsImRpc3BsYXlfbmFtZSI6IkppYW5CaW4gVGFuZyIsImlhdCI6MTY3NTgzNjE1OSwiZXhwIjoxNjc1ODc5MzIzfQ.Fys-4Vff4a5iyer9USSPT5ePdZvoKEJKKrIjsKPkptMyqd09KBFQX92ZYtz2Xu-aSgWyNkAZQEZCgfSEEWWpz8R2Oyk3PuCj4yi70sRcWCmdoj7poAG6D2YsGuq_KTf3ni9d2k5R3-OViY1wOBoJJvgHcMzunYJttblU-0BLW-srKj_NTsll5Zt62i6PLtGhhIQEtBpGIzqlqFFmXLedDVznaJTkYc7s6PTDe1W86b9WHvoBNPI3CHNrcMyJ69tT2EVcH0xZkoPeUxjOou1u2f33nZgdErNDfZVZ3Cww9XIhgvuPI13FMBzTIqMnSyEJ14ImEZrd2V-P2NkW1_3iLg’
'''

# TODO, cache
def authenticate_user_pwd(url, username,password):
    """Calls the authentication endpoint for Cloud Pak for Data as a Service,
    and returns authentication headers if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#creating-an-iam-bearer-token.

    Args:
        apikey (str): An IBM Cloud API key, obtained from https://cloud.ibm.com/iam/apikeys).
    Returns:
        success (bool): Whether authentication was successful
        headers (dict): If success=True, a dictionary with valid authentication headers. Otherwise, None.
        error_msg (str): The text response from the authentication request if the request failed.
    """
    auth_headers = {
        'cache-control': 'no-cache',
        'Content-Type': 'application/json'
    }

    data = {
        'username': username,
        'password': password,
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey'
    }

    r = requests.post( url + '/icp4d-api/v1/authorize', headers=auth_headers, data=data)

    if r.ok:
        headers = {"Authorization": "Bearer " + r.json()['access_token'], "content-type": "application/json"}
        return True, headers, ""
    else:
        return False, None, r.text

def get_user_token(url, username, password):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    payload = {"username": username, "password": password}
    body = json.dumps(payload)
    h = {"cache-control": "no-cache", "content-type": "application/json"}
    # r = (requests.post(url + "/icp4d-api/v1/authorize", data=body, headers=h, verify=False)).json()
    r = (requests.post(url + "/icp4d-api/v1/authorize", data=body, headers=h, verify=False))
    print('r=',r.json())

    if r.ok:
        headers = {"Authorization": "Bearer " + r.json()['token'], "content-type": "application/json"}
        return True, headers, ""
    else:
        return False, None, r.text

def list_projects(headers):
    """Calls the project list endpoint of Cloud Pak for Data as a Service,
    and returns a list of projects if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#projects-list.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
    Returns:
        projects (list): A list of (project_name, project_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{CPD_URL}/v2/projects", headers=headers, params={"limit": 100})
    print('r=', r.json())

    if r.ok:
        projects = r.json()['resources']
        parsed_projects = [(x['entity']['name'], x['metadata']['guid']) for x in projects]
        return parsed_projects, ""
    else:
        return list(), r.text

url = 'https://cpd-cpd-instance.anz-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud'
username =  'jbtang'
password = 'jbtang'

# auth_ok, headers, error_msg = authenticate_user_pwd(url,username,password)
#
# print('auth_ok=',auth_ok)
# print('headers=',headers)
# print('error_msg=',error_msg)

auth_ok, headers, error_msg = get_user_token(url, username, password)
print('auth_ok=',auth_ok)
print('headers=',headers)
print('error_msg=',error_msg)


list_projects(headers)