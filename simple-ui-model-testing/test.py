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

def list_projects(url, headers):
    """Calls the project list endpoint of Cloud Pak for Data as a Service,
    and returns a list of projects if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#projects-list.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
    Returns:
        projects (list): A list of (project_name, project_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{url}/v2/projects", headers=headers, params={"limit": 100})
    print('r=', r.json())

    if r.ok:
        projects = r.json()['resources']
        parsed_projects = [(x['entity']['name'], x['metadata']['guid']) for x in projects]
        return parsed_projects, ""
    else:
        return list(), r.text

def prediction(headers, endpoint, payload, precision=2):
    """Calls the synchronous deployment prediction endpoint of Cloud Pak for Data as a Service,
    checking the input schema if provided by model_details.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        space_id (str): Deployment Space to list deployments from.
        deployment_details (dict): Deployment details obtained from get_deployment_details()
        model_details (dict): Model/Function details obtained from get_deployment_details()
        payload (dict): Input data to predict, in {feature_name: value} format.
        precision (int): Number of floating points to round the predicted probability to. Defaults to 2.
    """

    r = requests.post(endpoint,
                      headers=headers,
                      json=payload
                     )
    if r.ok:
        # note here we are hardcoding prediction parsing for binary classification cases
        preds = r.json()
        proba = preds['predictions'][0]['values'][0][-1]
        if isinstance(proba, list):
            proba = max(proba)
        class_pred = preds['predictions'][0]['values'][0][-2]
        return (round(proba, precision), class_pred), ""
    else:
        print(r.text)
        return (None, None), r.text

url = 'https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud'
url = url.rstrip('/')
username =  'jbtang'
password = ''


# auth_ok, headers, error_msg = authenticate_user_pwd(url,username,password)
#
# print('auth_ok=',auth_ok)
# print('headers=',headers)
# print('error_msg=',error_msg)

auth_ok, headers, error_msg = get_user_token(url, username, password)
print('auth_ok=',auth_ok)
print('headers=',headers)
print('error_msg=',error_msg)


# list_projects(url,headers)

'''
headers= {'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ilo4LTNwd2RlMEdPbHZVc1VJWkw1cWJJVWZBTk5jVlZrMUFoQnNMenhERU0ifQ.eyJ1c2VybmFtZSI6ImpidGFuZyIsInJvbGUiOiJBZG1pbiIsInBlcm1pc3Npb25zIjpbImNyZWF0ZV9kYXNoYm9hcmQiLCJ2aWV3X2Rhc2hib2FyZCIsImNyZWF0ZV9wcm9qZWN0IiwiYWNjZXNzX2NhdGFsb2ciLCJjcmVhdGVfc3BhY2UiLCJtYW5hZ2VfZGlzY292ZXJ5Iiwidmlld19nb3Zlcm5hbmNlX2FydGlmYWN0cyIsImF1dGhvcl9nb3Zlcm5hbmNlX2FydGlmYWN0cyIsImFjY2Vzc19kYXRhX3F1YWxpdHlfYXNzZXRfdHlwZXMiLCJtYW5hZ2VfY2F0YWxvZyIsIm1hbmFnZV9yZXBvcnRpbmciLCJtb25pdG9yX3Byb2plY3QiLCJtYW5hZ2VfZ292ZXJuYW5jZV93b3JrZmxvdyIsIm1hbmFnZV9jYXRlZ29yaWVzIiwibWFuYWdlX2dsb3NzYXJ5IiwibWFuYWdlX3ZhdWx0c19hbmRfc2VjcmV0cyIsInNoYXJlX3NlY3JldHMiLCJhZGRfdmF1bHRzIiwiYWRtaW5pc3RyYXRvciIsImNhbl9wcm92aXNpb24iLCJtb25pdG9yX3BsYXRmb3JtIiwiY29uZmlndXJlX3BsYXRmb3JtIiwidmlld19wbGF0Zm9ybV9oZWFsdGgiLCJjb25maWd1cmVfYXV0aCIsIm1hbmFnZV91c2VycyIsIm1hbmFnZV9ncm91cHMiLCJtYW5hZ2Vfc2VydmljZV9pbnN0YW5jZXMiXSwiZ3JvdXBzIjpbMTAwMDIsMTAwMDQsMTAwMDBdLCJzdWIiOiJqYnRhbmciLCJpc3MiOiJLTk9YU1NPIiwiYXVkIjoiRFNYIiwidWlkIjoiMTAwMDMzMTAyNCIsImF1dGhlbnRpY2F0b3IiOiJkZWZhdWx0IiwiZGlzcGxheV9uYW1lIjoiSmlhbmJpbiBUYW5nIiwiYXBpX3JlcXVlc3QiOmZhbHNlLCJpYXQiOjE2OTk1MzEyODksImV4cCI6MTY5OTU3NDQ4OX0.Jz_3pKaOHWRhomoaw0KtWwiBJDj7UG397QdJvvxbgKAIbbDBWrz-nGlLsTy13gvdrRhgL5atJB6UHPb7ul40235fRQVnfplh-WZRsGBPkzHOL8B1HGox5i8pvA7rREe-UfU03FSZV2n77ej9OMLtzTeM6ebuAfTACLgcRidXaLassVdqvSmruheXEByGjgGhR7cQlK48YHphL_23SLAY4eAo0VkARlIuXaSo5cvLbOuLz7sn4KtP01BhdKzn8yPnMYvtyD73Bka984cfSIa1Zzj69vsdgrS8mxgRGym7nKNndoHqg3yf6hopWJaMvYr4NwRxIcCoWGLjh52oWS8u3A', 'content-type': 'application/json'}
prepared_payload =  {'input_data': [{'fields': ['age', 'job', 'marital', 'education', 'default', 'balance', 'housing', 'loan', 'contact', 'day', 'month', 'duration', 'campaign', 'pdays', 'previous', 'poutcome'], 'values': [[42, 'blue-collar', 'single', 'secondary', 'no', 1080, 'yes', 'yes', 'cellular', 13, 'may', 951, 3, 370, 4, 'failure']]}]}
endpoint = https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud/ml/v4/deployments/43b5ca09-a82a-46b4-a468-c055a9358401/predictions
'''
print('start predicting...')



endpoint = 'https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud/ml/v4/deployments/43b5ca09-a82a-46b4-a468-c055a9358401/predictions?version=2021-05-01'
# endpoint = 'https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud/ml/v4/deployments/43b5ca09-a82a-46b4-a468-c055a9358401/predictions'
payload_str = '{"input_data":[{"fields": ["age","job","marital","education","default","balance","housing","loan","contact","day", "month","duration","campaign","pdays","previous","poutcome"],"values": [[27,"unemployed", "married", "primary", "no",1787,"no", "no","cellular",19,"oct", 79, 1, -1, 0, "unknown" ]]}]}'

payload ={'input_data': [{'fields': ['age', 'job', 'marital', 'education', 'default', 'balance', 'housing', 'loan', 'contact', 'day', 'month', 'duration', 'campaign', 'pdays', 'previous', 'poutcome'], 'values': [[40, 'management', 'married', 'tertiary', 'no', -17, 'yes', 'yes', 'cellular', 11, 'may', 474, 1, 256, 1, 'success']]}]}
payload_str = json.dumps(payload)
print(payload_str)

import json

print(type(payload_str))

payload = json.loads(payload_str)
print(type(payload))

print('headers =',headers)
print('payload=',payload)
(proba, class_pred), error_msg = prediction(headers, endpoint, payload, precision=2)

print(proba, class_pred)
