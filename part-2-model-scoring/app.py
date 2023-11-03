import streamlit as st

from pages import data_exploration, model_testing

st.set_page_config(
    page_title="Model Inspection App",
    page_icon="🔎",
    layout="wide"
)

st.sidebar.header("Let's explore some data")
st.sidebar.markdown("""
Welcome to this Exploratory Data Analysis and Model Testing app.
""")


# st.header("Authenticate and pick a project and dataset")
# url = st.text_input("CPD URL", value="https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud",  type='default')
# username = st.text_input("username", value="jbtang", type='default')
# password = st.text_input("password", type='password')
#
# auth_ok, headers, error_msg = cpd_helpers.authenticate(url, username, password)

PAGE_MAP = {
    "Data Exploration": data_exploration,
    "Model Testing": model_testing
}

st.sidebar.header("Page Navigation")
current_page = st.sidebar.radio("Go To", list(PAGE_MAP), key='sidebar')
PAGE_MAP[current_page].write()

st.sidebar.markdown("""
## About
This app's goal is for a Data Scientist to share findings of the EDA phase of a project
to different project stakeholders, in an interactive fashion, as well as showcase the behavior
of candidate Machine Learning models trained on this data.

The data loaded here is stored and governed in a Watson Studio project on IBM Cloud. The models used are also trained
and deployed on Watson Studio. Learn more [here](https://www.ibm.com/cloud/watson-studio).
""")