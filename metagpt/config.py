#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provide configuration, singleton
"""
import os

import openai
import yaml
from google.cloud.firestore_v1 import FieldFilter

from metagpt.const import PROJECT_ROOT
from metagpt.logs import logger
from metagpt.tools import SearchEngineType, WebBrowserEngineType
from metagpt.utils.singleton import Singleton

import firebase_admin
from firebase_admin import credentials, firestore

# firebase_admin.initialize_app()
# db = firestore.client()
class NotConfiguredException(Exception):
    """Exception raised for errors in the configuration.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="The required configuration is not set"):
        self.message = message
        super().__init__(self.message)


class Config(metaclass=Singleton):
    """
    Regular usage method:
    config = Config("config.yaml")
    secret_key = config.get_key("MY_SECRET_KEY")
    print("Secret key:", secret_key)
    """

    _instance = None
    user_ref = None
    default_yaml_file = PROJECT_ROOT / "config/config.yaml"
    key_yaml_file = PROJECT_ROOT / "config/key.yaml"
    # firebase_admin.initialize_app()
    # db = firestore.client()
    #
    #
    # user_ref = db.collection("minions").where("userid", "==", "arunneo").limit(1)
    #
    # for agent in user_ref.get():
    #     # Access subcollection reference
    #     roles_ref = db.collection("minions").document(agent.id).collection("roles")
    #
    #     # # Filter and retrieve roles based on subcollection condition (optional)
    #     # filtered_roles = roles_ref.where("department", "==", "Marketing")
    #
    #     for role in roles_ref.get():
    #         # Access and process data from each role document
    #         role_data = role.to_dict()
    #         print(f"Role: {role_data['role_name']}")

    # for doc in docs:
    #     logger.info(doc.id)
    #     logger.info(str(doc.to_dict()))

    def __init__(self, yaml_file=default_yaml_file):
        self._configs = {}
        self._init_with_config_files_and_env(self._configs, yaml_file)
        logger.info("Config loading done.")
        self.global_proxy = self._get("GLOBAL_PROXY")
        # self.openai_api_key = self._get("OPENAI_API_KEY")
        # self.anthropic_api_key = self._get("Anthropic_API_KEY")
        # if (not self.openai_api_key or "YOUR_API_KEY" == self.openai_api_key) and (
        #         not self.anthropic_api_key or "YOUR_API_KEY" == self.anthropic_api_key
        # ):
        #     raise NotConfiguredException("Set OPENAI_API_KEY or Anthropic_API_KEY first")
        # self.openai_api_base = self._get("OPENAI_API_BASE")
        # openai_proxy = self._get("OPENAI_PROXY") or self.global_proxy
        # if openai_proxy:
        #     openai.proxy = openai_proxy
        #     openai.api_base = self.openai_api_base
        # self.openai_api_type = self._get("OPENAI_API_TYPE")
        # self.openai_api_version = self._get("OPENAI_API_VERSION")
        # self.openai_api_rpm = self._get("RPM", 3)
        # self.openai_api_model = self._get("OPENAI_API_MODEL", "gpt-4")
        self.max_tokens_rsp = self._get("MAX_TOKENS", 2048)
        # self.deployment_name = self._get("DEPLOYMENT_NAME")
        # self.deployment_id = self._get("DEPLOYMENT_ID")

        self.spark_appid = self._get("SPARK_APPID")
        self.spark_api_secret = self._get("SPARK_API_SECRET")
        self.spark_api_key = self._get("SPARK_API_KEY")
        self.domain = self._get("DOMAIN")
        self.spark_url = self._get("SPARK_URL")

        self.claude_api_key = self._get("Anthropic_API_KEY")
        self.serpapi_api_key = self._get("SERPAPI_API_KEY")
        self.serper_api_key = self._get("SERPER_API_KEY")
        self.google_api_key = self._get("GOOGLE_API_KEY")
        self.google_cse_id = self._get("GOOGLE_CSE_ID")
        self.search_engine = SearchEngineType(self._get("SEARCH_ENGINE", SearchEngineType.SERPAPI_GOOGLE))
        self.web_browser_engine = WebBrowserEngineType(self._get("WEB_BROWSER_ENGINE", WebBrowserEngineType.PLAYWRIGHT))
        self.playwright_browser_type = self._get("PLAYWRIGHT_BROWSER_TYPE", "chromium")
        self.selenium_browser_type = self._get("SELENIUM_BROWSER_TYPE", "chrome")
        self.gen_research_subsection = ""
        self.gen_research_questions = ""
        self.es_store = ""
        self.es_store_project = ""
        self.vertex_project=self._get("GCP_PROJECT_ID")
        self.vertex_location=self._get("GCP_LOCATION")
        self.vertex_model_regular_palm=self._get("GCP_MODEL_REGULAR_PALM")
        self.vertex_model_large_palm=self._get("GCP_MODEL_LARGE_PALM")
        self.vertex_model_gemini=self._get("GCP_MODEL_GEMINI")



        self.long_term_memory = self._get("LONG_TERM_MEMORY", False)
        if self.long_term_memory:
            logger.warning("LONG_TERM_MEMORY is True")
        self.max_budget = self._get("MAX_BUDGET", 10.0)
        self.total_cost = 0.0

        self.puppeteer_config = self._get("PUPPETEER_CONFIG", "")
        self.mmdc = self._get("MMDC", "mmdc")
        self.calc_usage = self._get("CALC_USAGE", True)
        self.model_for_researcher_summary = self._get("MODEL_FOR_RESEARCHER_SUMMARY")
        self.model_for_researcher_report = self._get("MODEL_FOR_RESEARCHER_REPORT")
        self.mermaid_engine = self._get("MERMAID_ENGINE", "nodejs")
        self.pyppeteer_executable_path = self._get("PYPPETEER_EXECUTABLE_PATH", "")

        self.prompt_format = self._get("PROMPT_FORMAT", "markdown")
        #self.setTaskConfig("arunneo", "CPG Product Research")

    def _init_with_config_files_and_env(self, configs: dict, yaml_file):
        """Load from config/key.yaml, config/config.yaml, and env in decreasing order of priority"""
        configs.update(os.environ)

        for _yaml_file in [yaml_file, self.key_yaml_file]:
            if not _yaml_file.exists():
                continue

            # Load local YAML file
            with open(_yaml_file, "r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                if not yaml_data:
                    continue
                os.environ.update({k: v for k, v in yaml_data.items() if isinstance(v, str)})
                configs.update(yaml_data)

    def _get(self, *args, **kwargs):
        return self._configs.get(*args, **kwargs)

    def get(self, key, *args, **kwargs):
        """Search for a value in config/key.yaml, config/config.yaml, and env; raise an error if not found"""
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(f"Key '{key}' not found in environment variables or in the YAML file")
        return value

    def setTaskConfig(self,userid,taskid):
        """Search for a value in config/key.yaml, config/config.yaml, and env; raise an error if not found"""

        self.gen_research_subsection = self._get("CPG_RESEARCH_SECTION")
        self.gen_research_questions = self._get("CPG_RESEARCH_QUESTIONS")

        self.es_store = self._get("GCP_ES_STORE")
        self.es_store_project = self._get("GCP_ES_PROJECT")

        # To Do Port all the Config into Fire Store for Dynamic Agent Configuration

        # user_ref = db.collection("minions").where(filter=FieldFilter("userid", "==", userid)).where(filter=FieldFilter("TaskDetails.TaskName", "==", taskid)).limit(1)
        # print(user_ref)
        # for agent in user_ref.get():
        #     # Access subcollection reference
        #     roles_ref = db.collection("minions").document(agent.id).collection("roles")
        #
        #     # # Filter and retrieve roles based on subcollection condition (optional)
        #     # filtered_roles = roles_ref.where("department", "==", "Marketing")
        #
        #     for role in roles_ref.get():
        #         # Access and process data from each role document
        #         role_data = role.to_dict()
        #         print(f"Role: {role_data['role_name']}")
        #         skills_ref = db.collection("minions").document(agent.id).collection("roles").document(role.id).collection("skills")
        #         for skill in skills_ref.get():
        #             skill_data = skill.to_dict()
        #             print(f"Skill: {skill_data['skill_name']}")
        #             skills_config_ref = db.collection("minions").document(agent.id).collection("roles").document(role.id).collection("skills").document(skill.id).collection("skillsConfig")
        #             for skill_config in skills_config_ref.get():
        #                 skill_config_data = skill_config.to_dict()
        #                 if(skill_data['skill_name']=="GenerateResearchQueries"):
        #                     print(f"Skill Config: {skill_config_data['config']['SUB_SECTION']}")
        #                     self.gen_research_subsection = skill_config_data['config']['SUB_SECTION']
        #                     self.gen_research_questions = skill_config_data['config']['NO_OF_QUESTIONS']
        #                 elif(skill_data['skill_name']=="VertexSearchAndSummarize"):
        #                     print(f"Skill Config: {skill_config_data['config']['ES_DATA_STORE']}")
        #                     self.es_store = skill_config_data['config']['ES_DATA_STORE']
        #                     self.es_store_project = skill_config_data['config']['PROJECT_ID']




CONFIG = Config()
