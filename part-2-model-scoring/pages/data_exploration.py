import streamlit as st
import cpd_helpers
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import numpy as np
from utils import format_tuples


def write_df_sample(df):
    n_rows = st.number_input("Number of rows", min_value=0, max_value=len(df), value=min(5, len(df)), help='How many rows to sample and display.')
    sample_strategy = st.radio("How to pick rows", ["Random Sample", "Head"])
    if sample_strategy == "Random Sample":
        st.write(df.sample(int(n_rows)))
    else:
        st.write(df.head(int(n_rows)))


def write_viz_1(df, x_feature, label):
    st.subheader("Univariate distributions per class")
    if len(df) == 0:
        st.warning("The dataset loaded seems empty. Please try again")
        return
    st.plotly_chart(px.histogram(df, x=x_feature, color=label, marginal='box'))


def write_viz_2(df, x_feature, label):
    st.subheader("Average default rate per feature bin")
    st.markdown("This plot shows on the x axis a selected feature binned by quantile, \
        and on the y axis the average rate of the label's positive class in each bin. \
        The size of the bins can be selected with the slider below.")
    if len(df) == 0:
        st.warning("The dataset loaded seems empty. Please try again")
        return
    q_length = st.slider("Quantile size", min_value=0.01, max_value=0.5, step=0.01, value=0.05)
    bins = pd.qcut(df[x_feature], np.arange(0, 1.01, q_length), duplicates='drop')
    rate_per_bin = df.groupby(bins)[label].value_counts(normalize=True)
    fig, ax = plt.subplots()
    rate_per_bin.unstack().plot(kind='bar', stacked=True, ax=ax, rot=45)
    # adjust tick alignments, see https://stackoverflow.com/questions/35262475/controlling-tick-labels-alignment-in-pandas-boxplot-within-subplots
    plt.sca(ax)
    plt.xticks(ha='right')
    ax.set_xlabel(f"Bins of feature {x_feature}")
    ax.set_ylabel(f"Average rate of label {label}")
    st.pyplot(fig)


def write():
    st.header("Authenticate and pick a project and dataset")
    url = st.text_input("CPD URL",
                        value="https://cpd-cpd47x.anz-tech-cpd-3d4f8f67f80aab8513fb91608489ed31-0000.au-syd.containers.appdomain.cloud",
                        type='default')
    url = url.rstrip('/')
    username = st.text_input("username", value="jbtang", type='default')
    password = st.text_input("password", type='password')

    auth_ok, headers = st.session_state.get('auth_ok', False), st.session_state.get('headers')

    if not auth_ok:
        auth_ok, headers, error_msg = cpd_helpers.authenticate(url, username, password)

        # store auth information in the session for other pages to re-use:
        st.session_state['auth_ok'] = auth_ok
        st.session_state['headers'] = headers
        st.session_state['url'] = url

    if not auth_ok:
        st.error("You could not be authenticated. More details below.")
        with st.expander("Expand to see the error message"):
            st.write(error_msg)
    else:
        st.success("You are successfully authenticated! Pick a project below.")

        projects, error_msg = cpd_helpers.list_projects(url, headers)
        if projects:
            _, project_id = st.selectbox("Pick a Watson Studio Project", projects, format_func=format_tuples)
        else:
            project_id = None
            st.warning("Oops! Looks like you don't have any project yet. \
                Check out [Creating a project](https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/projects.html?context=cpdaas&audience=wdp)")

    if not auth_ok or (project_id is None):
        st.write("Please authenticate and pick a project first.")
    else:
        datasets, error_msg = cpd_helpers.list_datasets(url, headers, project_id)
        if datasets:
            _, dataset_id = st.selectbox("Pick a Dataset to analyze", datasets, format_func=format_tuples)
            df = st.session_state.get('df')
            if auth_ok:
                df, error_msg = cpd_helpers.load_dataset(url, headers, project_id, dataset_id)

        # print('JB DF shape=',df.shape)

                st.session_state['df'] = df  # used on other pages

            st.header("Dataset preview")
            if not (auth_ok):
                st.write("Please authenticate and load a dataset first.")
            else:
                write_df_sample(df)

            st.header("Visualizations")
            if not (auth_ok ):
                st.write("Please authenticate and load a dataset first.")
            else:
                label = st.selectbox("Label column", list(df.columns))
                features = [c for c in df.columns if c != label]
                x_feature = st.selectbox("Feature (X axis)", features)

                write_viz_1(df, x_feature, label)
                # write_viz_2(df, x_feature, label)

        else:
            st.warning("Oops! Looks like there are no datasets in your project yet.")


