import streamlit as st
import time
import numpy as np
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="CPG Robo Agent Dossier Generator", page_icon="🗓️")

st.markdown("# Minion Researcher Agent")
st.write(
    """This demo illustrates the CPG Robo Assistant Dossier Creator, which takes several documents and creates a executive Dossier"""
)


last_rows = np.random.randn(1, 1)

with st.form(key='eval', clear_on_submit=True):
    #     uploaded_file = st.file_uploader(
    #         "Upload file", type=["pdf"],
    #         help="Only PDF files are supported",
    #         )
    topic_option = st.selectbox(
        'Please Choose the Research Topic', 
        ('New Product Research for Dish Detergent' , 'Product Research for Dish Detergent')
    )
    task_option = st.selectbox(
        'Please Choose the Task you want to Run',
        ('CPG Product Research', 'CPG Market Research'))
    # sub_section = st.multiselect('Select Documents for Research', SERIES.keys(), format_func=lambda y: SERIES[y],
    #                            help="Research Documents")


    submit_eval_button = st.form_submit_button(label='Perform My Task')

    if submit_eval_button:

            # clear_submit()
        with st.spinner("Your Minion @ Work"):
            data = {'name': "Sample Run", 'topic': topic_option, 'userid': "arunneo", 'task_id': task_option}
            with open("static/logs.html", 'r') as f:
                logs = f.read()

            with st.expander("Minion Worker Logs"):
                components.html(logs, height=400, scrolling=True)

            data = requests.post("http://localhost:8010/agent/run", json=data).json()

        with st.expander("QnA"):
                with open(f"../data/research/{topic_option} QnA.md", "r") as f:
                    md_text = f.read()
                dossier = st.markdown(md_text)

        with st.expander("Dossier"):
            with open(f"../data/research/{topic_option}_Dossier.md", "r") as f:
                    md_text = f.read()
            dossier = st.markdown(md_text)

        with st.expander("Concept Development Document"):
            with open(f"../data/research/{topic_option}_ConceptDevelopment.md", "r") as f:
                    md_text = f.read()
            dossier = st.markdown(md_text)
