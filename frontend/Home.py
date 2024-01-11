"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : Home.py
@Descriptor: This is the Web frontend for Demonstrating the Multi Agent LLM Framework
"""



from typing import List, Optional
from tenacity import retry, stop_after_attempt
import requests
import streamlit as st
import logging
import pandas as pd
import streamlit.components.v1 as components
import base64
import typing
import vertexai
from google.cloud import aiplatform, aiplatform_v1
from google.protobuf import struct_pb2

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
PROJECT_ID="greenfielddemos"
vertexai.init(project="greenfielddemos", location="us-central1")

    # Page layout
st.set_page_config(
        page_title="Cymbal CPG Product Research Innovation Engine",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded",

    )


col1, col2 = st.columns(2)

# Start of UI Components

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css" integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">'
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.css",crossorigin="anonymous">',
    unsafe_allow_html=True)

st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js" integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.min.js" integrity="sha384-+sLIOodYLS7CIrQpBjl+C7nPvqq+FbNUBDunl/OZv93DB7Ln/533i8e/mZXLi/P+" crossorigin="anonymous"></script>
""", unsafe_allow_html=True)

st.markdown("""

<nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #253662;">
  <a class="navbar-brand" href="https://cloud.google.com/ai/generative-ai" target="_blank">Cymbal Product Research  Demo</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

</nav>

 <style>
    div.stButton > button:first-child {
        background-color: #769449
        color:#000000;
    }
    div.stButton > button:hover {
        background-color: #F5F5F5;
        color:#000000;
        }
    div.stDownloadButton > button:first-child {
        background-color: #88cc23;
        color:#000000;
    }
    div.stDownloadButton > button:hover {
        background-color: #F5F5F5;
        color:#000000;
        }


    </style>
""", unsafe_allow_html=True)

st.markdown('''
<style>
.stApp header {
    z-index: 0;
}
</style>
''', unsafe_allow_html=True)



st.markdown(
                """
                
                ## Overview 
                
                Welcome to Cymbal Product Research & Innovation Assistant app , powered by Google LLM.
                **👈 Select a tasks from the sidebar** to see some demonstration
                of what Google LLM can do!
                
                While Artificial General Intelligence (AGI) for enterprise customers remains largely theoretical, 
                it promises to revolutionize businesses by mimicking human-like reasoning and decision-making across diverse tasks, 
                from researcher documents , to generating new product ideas.
                
                The following prototype demonstrates the capability of using LLM as personal assistants to mimic human tasks in the area of
                CPG research. The following picture depicts the user journey for a typical CPG company starting off the New Product Research study , from ideation to
                Concept development.
                
                

            """

)

st.image("../data/images/cpg_product_research.png")

st.markdown(
    """
   ## Conceptual Approach
   
   The current prototype explores LLM-based multi-agent systems, spotlighting the framework, MetaGemini, and its potential as multi-agent systems, 
   to replicate and enhance human workflows as described in the above schematic.
   
   The idea is to prove fostering of effective collaboration, both conversationally and through tool-based interactions. The diagram below highlights the representation of
   human tasks.We know that, through prolonged collaborative practice, humans have developed widely accepted Standardized Operating Procedures (SOPs) across various domains.

   These SOPs, which play a pivotal role in task decomposition and efficient coordination, ensure tasks are executed consistently and accurately, aligning with defined roles and quality standards.
   
   
"""

)
st.image("../data/images/Minions.png")

st.markdown(
    """
   
  In this prototype we represent a metaprogramming approach that coordinates LLM-based multi-agent systems, encoding SOPs into prompts and injects dynamically during agent invocation. 
  Specifically, MetaGemini manages multi-agents through role definition, task decomposition, process standardization, and other technical designs, completing the end-to-end development process with just a one-line requirement.
  I have customized the MetaGemini to enable Gemini and Palm as the LLM provider to perform automated assistant tasks.


"""

)
st.image("../data/images/flow_chart.png")


