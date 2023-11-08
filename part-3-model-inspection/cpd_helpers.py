import requests
import pandas as pd
import streamlit as st
import json
from urllib3.exceptions import InsecureRequestWarning

CPD_URL = "https://api.dataplatform.cloud.ibm.com"  # endpoint for anything data-related
WML_URL = "https://us-south.ml.cloud.ibm.com"  # endpoint for ML serving


# TODO, cache
def authenticate(cpd_url, username, password):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    payload = {"username": username, "password": password}
    body = json.dumps(payload)
    h = {"cache-control": "no-cache", "content-type": "application/json"}
    # r = (requests.post(cpd_url + "/icp4d-api/v1/authorize", data=body, headers=h, verify=False)).json()
    r = (requests.post(cpd_url + "/icp4d-api/v1/authorize", data=body, headers=h, verify=False))
    print('r=',r.json())

    if r.ok:
        headers = {"Authorization": "Bearer " + r.json()['token'], "content-type": "application/json"}
        return True, headers, ""
    else:
        return False, None, r.text

@st.cache_data
def list_projects(cpd_url, headers):
    """Calls the project list endpoint of Cloud Pak for Data as a Service,
    and returns a list of projects if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#projects-list.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
    Returns:
        projects (list): A list of (project_name, project_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{cpd_url}/v2/projects", headers=headers, params={"limit": 100})
    if r.ok:
        projects = r.json()['resources']
        parsed_projects = [(x['entity']['name'], x['metadata']['guid']) for x in projects]
        return parsed_projects, ""
    else:
        print(r.text)
        return list(), r.text


@st.cache_data
def list_datasets(cpd_url, headers, project_id):
    """Calls the search endpoint of Cloud Pak for Data as a Service,
    and returns a list of data assets in a given project if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#simplesearch.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        project_id (str): The Watson Studio project id to search in.
    Returns:
        datasets (list): A list of (dataset_name, dataset_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    search_doc = {
        "query": {
            "bool": {
                "must": 
                [
                    {"match": {"metadata.artifact_type": "data_asset"}},
                    {"match": {"entity.assets.project_id": project_id}}
                ]
            }
        }
    }
    r = requests.post(f"{cpd_url}/v3/search",
                      headers=headers,
                      json=search_doc)

    if r.ok:
        datasets = r.json()['rows']
        parsed_datasets = [(x['metadata']['name'], x['artifact_id']) for x in datasets]
        return parsed_datasets, ""
    else:
        print(r.text)
        return list(), r.text


@st.cache_data
def load_dataset(cpd_url, headers, project_id, dataset_id):
    """Loads into a memory a data asset stored in a Watson Studio project
    on IBM Cloud Pak for Data as a Service.
    Abstracts away three steps:
    - Retrieving a details of a data asset including its attachment id
    - Retrieving the attachment
    - Extracting a signed url from the attachment and using it to load the data into Pandas

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        project_id (str): The Watson Studio project id to search in.
        dataset_id (str): The dataset to load
    Returns:
        df (pd.DataFrame): The dataset loaded into a Pandas DataFrame, empty if any of the HTTP requests fails.
        error_msg (str): If any of the HTTP requests fails, the text response from the first failing
            request.
    """
    r = requests.get(f"{cpd_url}/v2/data_assets/{dataset_id}",
                     params={"project_id": project_id},
                     headers=headers
                    )
    if r.ok:
        dataset_details = r.json()
        if dataset_details['entity']['data_asset']['mime_type'] != 'text/csv':
            st.warning("The dataset selected is not in CSV format and cannot be loaded. Please select another one.")
        attachment_id = dataset_details['attachments'][0]['id']
    else:
        print(r.text)
        return pd.DataFrame(), r.text

    r2 = requests.get(f"{cpd_url}/v2/assets/{dataset_id}/attachments/{attachment_id}",
                      params={"project_id": project_id},
                      headers=headers
                      )
    if r2.ok:
        attachment_details = r2.json()
    else:
        return pd.DataFrame(), r2.text

    try:
        # print('attachment_details=', attachment_details)

        df_url = f"{cpd_url}{attachment_details['url']}"
        # print('df_url = ', df_url)
        df = pd.read_csv(df_url)

        return df, ""
    except Exception as e:
        return pd.DataFrame(), str(e)


@st.cache_data
def list_spaces(cpd_url, headers):
    """Calls the spaces list endpoint of Cloud Pak for Data as a Service,
    and returns a list of projects if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#projects-list, /v2/spaces
    is built similarly to /v2/projects.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
    Returns:
        spaces (list): A list of (space_name, space_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{cpd_url}/v2/spaces", headers=headers)
    if r.ok:
        spaces = r.json()['resources']
        parsed_projects = [(x['entity']['name'], x['metadata']['id']) for x in spaces]
        return parsed_projects, ""
    else:
        print(r.text)
        return list(), r.text


@st.cache_data
def list_deployments(wml_url, headers, space_id):
    """Calls the deployments list endpoint of Cloud Pak for Data as a Service,
    and returns a list of deployments if successful.
    See https://cloud.ibm.com/apidocs/machine-learning#deployments-list.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        space_id (str): Deployment Space to list deployments from.
    Returns:
        deployments (list): A list of (project_name, project_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{wml_url}/ml/v4/deployments",
                     headers=headers,
                     params={"space_id": space_id, "version": "2021-01-01"}
    )
    if r.ok:
        deployments = r.json()['resources']
        parsed_deployments = [(x['entity']['name'], x['metadata']['id']) for x in deployments]
        return parsed_deployments, ""
    else:
        print(r.text)
        return list(), r.text


@st.cache_data
def get_deployment_details(wml_url, headers, space_id, deployment_id):
    """Calls the deployment details endpoint of Cloud Pak for Data as a Service,
    then calls the model (resp. function) details for the model (resp. function)
    associated with this deployment.
    See:
    - https://cloud.ibm.com/apidocs/machine-learning#deployments-get
    - https://cloud.ibm.com/apidocs/machine-learning#functions-get
    - https://cloud.ibm.com/apidocs/machine-learning#models-get

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        space_id (str): Deployment Space to list deployments from.
        deployment_id (str): Id of the deployment selected
    Returns:
        # TODO
    """
    r = requests.get(f"{wml_url}/ml/v4/deployments/{deployment_id}",
                     headers=headers,
                     params={"space_id": space_id, "version": "2021-01-01"}
    )
    if r.ok:
        deployment_details = r.json()
        asset_id = deployment_details['entity']['asset']['id']
        asset_type = deployment_details['entity']['deployed_asset_type']  # "model" or "function"

        r2 = requests.get(f"{wml_url}/ml/v4/{asset_type}s/{asset_id}",
                          headers=headers,
                          params={"space_id": space_id, "version": "2021-01-01"}
        )

        if r2.ok:
            asset_details = r2.json()
            return deployment_details, asset_details, ""
        else:
            print(r2.text)
            return deployment_details, dict(), r2.text
    else:
        print(r.text)
        return dict(), dict(), r.text


def prepare_input_schema(model_details, payload):
    """Helper function that checks that a given payload follows the input schema
    of a given model, and filter input columns if needed.

    Args:
        model_details (dict): Model/Function details obtained from get_deployment_details()
        payload (dict): Input data to predict, in {feature_name: value} format.
    """
    if model_details.get('entity', dict()).get('schemas'):
        # model has an attached input schema (e.g. AutoAI, SPSS, or Python if user specified it)
        input_schema = model_details['entity']['schemas']['input'][0]
        expected_input_cols = [x['name'] for x in input_schema['fields']]
        return {k: v for k, v in payload.items() if k in expected_input_cols}
    else:
        return payload


# @st.cache(suppress_st_warning=True)
def get_deployment_prediction(headers, deployment_details, payload, precision=2):
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
    if not deployment_details.get('entity'):
        return

    # WML payloads are structured such that multiple mini-batches of data to scored can be passed,
    # each as a list of lists (i.e. a matrix) passed under input_data.values:
    prepared_payload = {
        "input_data": [{
            "fields": list(payload.keys()),
            "values": [list(payload.values())]}]
    }
    r = requests.post(deployment_details['entity']['status']['serving_urls'][0],
                      headers=headers,
                      json=prepared_payload,
                      params={"version": "2021-01-01"}
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


@st.cache(suppress_st_warning=True)
def list_jobs(cpd_url, headers, project_id):
    """Calls the jobs list endpoint of Cloud Pak for Data as a Service,
    and returns a list of jobs if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#jobs-list.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        project_id (str): Project to list jobs from.
    Returns:
        jobs (list): A list of (job_name, job_id) tuples.
        error_msg (str): The text response from the request if the request failed.
    """
    r = requests.get(f"{cpd_url}/v2/jobs",
                     headers=headers,
                     params={"project_id": project_id}
    )
    if r.ok:
        jobs = r.json()['results']
        parsed_jobs = [(x['metadata']['name'], x['metadata']['asset_id']) for x in jobs]
        return parsed_jobs, ""
    else:
        print(r.text)
        return list(), r.text


def trigger_job(cpd_url, headers, project_id, job_id, env_variables):
    """Calls the jobrun trigger endpoint of Cloud Pak for Data as a Service,
    and returns jobrun details if successful.
    See https://cloud.ibm.com/apidocs/watson-data-api#job-runs-create.

    Jobs receive parameters as environment variables, which this function receives
    as dictionary and formats properly as a list of "key1=value1" strings.

    Args:
        headers (dict): Authentication headers obtained with authenticate().
        project_id (str): Project where the job lives.
        job_id (str): Id of the job to create a jobrun for.
        env_variables (dict): Dictionary of key,values to pass as environment variables.
    Returns:
        jobrun_details (dict): Dictionary containing details of the jobrun triggered.
        error_msg (str): The text response from the request if the request failed.
    """
    jobrun_config = {
        "job_run": {
            "configuration": {
                "env_variables": env_variables
            }
        }
    }
    env_variables = [f"{key}={value}" for key, value in env_variables.items() if key != ""]
    r = requests.post(f"{cpd_url}/v2/jobs/{job_id}/runs",
                        headers=headers,
                        json=jobrun_config,
                        params={'project_id': project_id}
                        )
    if r.ok:
        jobrun_info = r.json()
        # jobrun_id = jobrun_info['metadata']['asset_id']
        return jobrun_info, ""
    else:
        print(r.text)
        return dict(), r.text
