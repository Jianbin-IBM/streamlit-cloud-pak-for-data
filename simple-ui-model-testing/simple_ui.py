import streamlit as st
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

def authenticate_user_pwd(url, username, password):
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

    r = requests.post(url + '/icp4d-api/v1/authorize', headers=auth_headers, data=data, verify=False)

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
    # print('r=', r.json())

    if r.ok:
        headers = {"Authorization": "Bearer " + r.json()['token'], "content-type": "application/json"}
        return True, headers, ""
    else:
        return False, None, r.text


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
                      json=payload, verify=False
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
        # print(r.text)
        return (None, None), r.text


st.header("Authentication")
url = st.text_input("CPD URL", value="https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud",  type='default')
url = url.rstrip('/')
username = st.text_input("username", value="jbtang", type='default')
password = st.text_input("password", type='password')

auth_ok, headers, error_msg = get_user_token(url, username, password)

if not auth_ok:
    st.info("You are not authenticated yet.")
else:
    st.success("You are successfully authenticated! You can copy your ML endpoint below to use your model")

st.header("Test Deployed Model")
#model_endpoint_2 = st.text_area("Deployed ML Model Endpoint", value="https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud/ml/v4/deployments/43b5ca09-a82a-46b4-a468-c055a9358401/predictions?version=2021-05-01")
model_endpoint_2 = st.text_area("Deployed ML Model Endpoint",
                                value="")
input_json_2 = st.text_area("Input JSON", height=150, value='{"input_data":[{"fields": ["age","job","marital","education","default","balance","housing","loan","contact","day", "month","duration","campaign","pdays","previous","poutcome"],"values": [[27,"unemployed", "married", "primary", "no",1787,"no", "no","cellular",19,"oct", 79, 1, -1, 0, "unknown" ]]}]}')

button = st.button("Prediction")
if button:
    payload = json.loads(input_json_2)
    # print(type(payload))
    # print('headers =',headers)
    # print('payload=',payload)
    (proba, class_pred), error_msg = prediction(headers, model_endpoint_2, payload, precision=2)

    #print(proba, class_pred)

    st.metric("Probability", proba)
    st.metric("Predicted Class", class_pred)

