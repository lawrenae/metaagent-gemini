import streamlit as st
import time
import numpy as np

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter


st.set_page_config(page_title="CPG Robo Agent Configurator", page_icon="☕")

st.markdown("# Configurator Screen")
st.write(
    """This demo illustrates the CPG Robo Assistant Configurator"""
)

if 'task_actions' not in st.session_state:
    st.session_state['task_actions'] = ''

# def init_firebase():
#   # Your Firebase initialization logic
#   firebase_app = firebase_admin.initialize_app()
#   return firebase_app
#
# if "firebase_app" not in st.session_state:
#   st.session_state.firebase_app = init_firebase()
#
# # Use the initialized app instance
# firebase_app = st.session_state.firebase_app
# db = firestore.client()

# def getTaskConfig(self, userid, taskid):
#     """Search for a value in config/key.yaml, config/config.yaml, and env; raise an error if not found"""
#     user_ref = db.collection("minions").where(filter=FieldFilter("userid", "==", userid)).where(
#         filter=FieldFilter("TaskDetails.TaskName", "==", taskid)).limit(1)
#
#     for agent in user_ref.get():
#         # Access subcollection reference
#         roles_ref = db.collection("minions").document(agent.id).collection("roles")
#
#         # # Filter and retrieve roles based on subcollection condition (optional)
#         # filtered_roles = roles_ref.where("department", "==", "Marketing")
#
#         for role in roles_ref.get():
#             # Access and process data from each role document
#             role_data = role.to_dict()
#             print(f"Role: {role_data['role_name']}")
#             skills_ref = db.collection("minions").document(agent.id).collection("roles").document(role.id).collection(
#                 "skills")
#             for skill in skills_ref.get():
#                 skill_data = skill.to_dict()
#                 print(f"Skill: {skill_data['skill_name']}")
#                 skills_config_ref = db.collection("minions").document(agent.id).collection("roles").document(
#                     role.id).collection("skills").document(skill.id).collection("skillsConfig")
#                 for skill_config in skills_config_ref.get():
#                     skill_config_data = skill_config.to_dict()
#                     if (skill_data['skill_name'] == "GenerateResearchQueries"):
#                         print(f"Skill Config: {skill_config_data['config']['SUB_SECTION']}")
#                         self.gen_research_subsection = skill_config_data['config']['SUB_SECTION']
#                         self.gen_research_questions = skill_config_data['config']['NO_OF_QUESTIONS']
#                     elif (skill_data['skill_name'] == "VertexSearchAndSummarize"):
#                         print(f"Skill Config: {skill_config_data['config']['ES_DATA_STORE']}")
#                         self.es_store = skill_config_data['config']['ES_DATA_STORE']
#                         self.es_store_project = skill_config_data['config']['PROJECT_ID']

last_rows = np.random.randn(1, 1)
# with st.form(key='eval', clear_on_submit=True):
    #     uploaded_file = st.file_uploader(
    #         "Upload file", type=["pdf"],
    #         help="Only PDF files are supported",
    #         )

industry_option = st.selectbox(
        'What industry you belong to',
        ['CPG'])

role_option = st.selectbox(
        'What is your Role',
        ['Product Researcher','Global Marketing Manager'])



def set_taskactions(tasks):

        if (tasks == "Product Research"):
            st.session_state['task_actions'] = ['GenerateResearchQueries', 'VertexSearchAndSummarize', 'ConductResearch']

        else:
            st.session_state['task_actions'] = ['WebpageBrowse&Summarize', 'PrivateDataBrowse&Summarize', 'ProductReviewsInsight',
                 'Research Dossier Generator']


def set_task_properties(tasks_actions):

        if 'GenerateResearchQueries' in tasks_actions:
            col1, col2 = st.columns(2)
            with col1:
                task_property_1 = st.multiselect('Research Topic Subsections',
                                               ['Core functions', 'ideal product/service/experience',
                                                'consumer satisfaction', 'current gaps', 'market trends', 'market size',
                                                'key technology and scientific advancements'])
            with col2:
                task_property_2 = st.text_input('Research Topic Questions per Section', 2)

        elif 'VertexSearchAndSummarize' in tasks_actions:
            task_property_1 = task_property_1 = st.selectbox('VertexAI Data Source',
                                                             ['cpg-research-docs-v1_1701270367059'])

tasks = st.selectbox(
        'What are the tasks you would like to perform',key="tasks",
        options=['Product Market Research', 'Product Research', 'Product Reviews'])
selected_value = st.session_state.tasks

# Do something with the selected value
st.write(f"You selected: {selected_value}")

set_taskactions(selected_value)

if(st.session_state['task_actions']!=""):
    tasks_actions = st.multiselect(
            'Please choose the tasks skills to perform the task listed above',
            options=st.session_state['task_actions'], key="tasks_actions")

set_task_properties(st.session_state.task_actions)







submit_eval_button = st.button(label='Configure Assistant')

if submit_eval_button:
        progress_bar = st.progress(0)
        status_text = st.empty()
            # clear_submit()
        for i in range(1, 101):
                new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
                status_text.text("✅ %i%% Complete" % i)
                progress_bar.progress(i)
                last_rows = new_rows
                time.sleep(0.05)

        progress_bar.empty()


