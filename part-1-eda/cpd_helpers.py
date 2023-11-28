# CPD API reference: https://cloud.ibm.com/apidocs/cloud-pak-data/cloud-pak-data-4.5.0#getauthorizationtoken
# Watson Data API: https://cloud.ibm.com/apidocs/watson-data-api-cpd#other-assets-api-objects

import requests
import pandas as pd
import json
from urllib3.exceptions import InsecureRequestWarning

from io import StringIO
def read_csv_from_url(url):
    try:
        # Download the CSV file from the URL with certificate verification disabled
        response = requests.get(url, verify=False)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Use pandas to read the CSV directly from the response content
            df = pd.read_csv(StringIO(response.text))
            return df
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# TODO, cache
def authenticate(cpd_url, username, password):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    payload = {"username": username, "password": password}
    body = json.dumps(payload)
    h = {"cache-control": "no-cache", "content-type": "application/json"}
    # r = (requests.post(cpd_url + "/icp4d-api/v1/authorize", data=body, headers=h, verify=False)).json()
    r = (requests.post(cpd_url + "/icp4d-api/v1/authorize", data=body, headers=h, verify=False))
    # print('r=',r.json())

    if r.ok:
        headers = {"Authorization": "Bearer " + r.json()['token'], "content-type": "application/json"}
        return True, headers, ""
    else:
        return False, None, r.text

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
    r = requests.get(f"{cpd_url}/v2/projects", headers=headers, params={"limit": 100}, verify=False)
    if r.ok:
        projects = r.json()['resources']
        parsed_projects = [(x['entity']['name'], x['metadata']['guid']) for x in projects]
        return parsed_projects, ""
    else:
        return list(), r.text

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
                      json=search_doc, verify=False)

    if r.ok:
        datasets = r.json()['rows']
        parsed_datasets = [(x['metadata']['name'], x['artifact_id']) for x in datasets]
        return parsed_datasets, ""
    else:
        return list(), r.text


# TODO cache
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
                     headers=headers, verify=False
                    )
    if r.ok:
        dataset_details = r.json()
        attachment_id = dataset_details['attachments'][0]['id']
    else:
        return pd.DataFrame(), r.text

    r2 = requests.get(f"{cpd_url}/v2/assets/{dataset_id}/attachments/{attachment_id}",
                      params={"project_id": project_id},
                      headers=headers, verify=False
                      )
    if r2.ok:
        attachment_details = r2.json()
    else:
        return pd.DataFrame(), r2.text

    try:
        #print('attachment_details=', attachment_details)
        df_url = f"{cpd_url}{attachment_details['url']}"
        #print('df_url = ', df_url)
        #df = pd.read_csv(df_url)
        df = read_csv_from_url(df_url)

        return df, ""

        #return pd.read_csv(attachment_details['url']), ""
    except Exception as e:
        return pd.DataFrame(), str(e)
