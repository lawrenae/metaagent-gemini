"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : google_palm_api.py
"""


import asyncio
import time
from typing import Optional,NamedTuple, Union
import base64
import vertexai.preview
from vertexai.preview.language_models import TextGenerationModel
from typing import Optional
from metagpt.config import CONFIG
from metagpt.logs import logger

from google.cloud import aiplatform

from metagpt.utils.token_counter import get_max_completion_tokens

aiplatform.constants.base.API_BASE_PATH = "autopush-aiplatform.sandbox.googleapis.com"
aiplatform.constants.base.PREDICTION_API_BASE_PATH = "autopush-aiplatform.sandbox.googleapis.com"

from vertexai.preview import generative_models
from vertexai.preview.generative_models import GenerativeModel, Image, Content, Part

from google.cloud import discoveryengine_v1beta
from google.cloud.discoveryengine_v1beta.services.search_service import pagers
from google.protobuf.json_format import MessageToDict
import json
from langchain.agents import AgentType, initialize_agent, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.chains.base import Chain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains import LLMChain, RetrievalQA, RetrievalQAWithSourcesChain
from langchain.llms import VertexAI
from langchain.llms.utils import enforce_stop_tokens
from langchain.prompts import PromptTemplate
from langchain.prompts import StringPromptTemplate
from langchain.retrievers import (
    GoogleVertexAIMultiTurnSearchRetriever,
    GoogleVertexAISearchRetriever,
)
from langchain.schema import AgentAction, AgentFinish, Document, BaseRetriever
from langchain.tools import Tool
from langchain.utils import get_from_dict_or_env
from pydantic import BaseModel, Extra, Field, root_validator
import re
from typing import Any, Mapping, List, Dict, Optional, Tuple, Sequence, Union
import unicodedata
from metagpt.utils.singleton import Singleton
from metagpt.utils.token_counter import (
    TOKEN_COSTS,
    count_message_tokens,
    count_string_tokens,
    get_max_completion_tokens,
)


class RateLimiter:
    """Rate control class, each call goes through wait_if_needed, sleep if rate control is needed"""

    def __init__(self, rpm):
        self.last_call_time = 0
        # Here 1.1 is used because even if the calls are made strictly according to time,
        # they will still be QOS'd; consider switching to simple error retry later
        self.interval = 1.1 * 60 / rpm
        self.rpm = rpm

    def split_batches(self, batch):
        return [batch[i : i + self.rpm] for i in range(0, len(batch), self.rpm)]

    async def wait_if_needed(self, num_requests):
        current_time = time.time()
        elapsed_time = current_time - self.last_call_time

        if elapsed_time < self.interval * num_requests:
            remaining_time = self.interval * num_requests - elapsed_time
            logger.info(f"sleep {remaining_time}")
            await asyncio.sleep(remaining_time)

        self.last_call_time = time.time()


class EnterpriseSearchChain(Chain):
    """Chain that queries an Enterprise Search Engine and summarizes the responses."""

    chain: Optional[LLMChain]
    search_client: Optional[GoogleVertexAISearchRetriever]

    def __init__(self,
                 project,
                 search_engine,
                 chain,
                 location='us',
                 serving_config_id='default_config'):
        super().__init__()
        self.chain = chain
        self.search_client = GoogleVertexAISearchRetriever( project_id=project,
    location_id=location,
    data_store_id=search_engine,
    max_documents=3,
                                                            max_extractive_answer_count=3,
                                                            get_extractive_answers=True,
                                                            )

    @property
    def input_keys(self) -> List[str]:
        return ['query']

    @property
    def output_keys(self) -> List[str]:
        return ['summary']

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        _run_manager = CallbackManagerForChainRun.get_noop_manager()
        query = inputs['query']
        _run_manager.on_text(query, color="green", end="\n", verbose=self.verbose)
        documents = self.search_client.get_relevant_documents(query)
        content = [d.page_content for d in documents]
        _run_manager.on_text(content, color="white", end="\n", verbose=self.verbose)
        summary = self.chain.run(content)
        return {'summary': summary}


    @property
    def _chain_type(self) -> str:
        return "google_enterprise_search_chain"

class Palm2:
    PROJECT_ID = CONFIG.vertex_project  # @param
    LOCATION = CONFIG.vertex_location  # @param
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 1024,
        "temperature": 0,
        "top_p": 0.8,
        "top_k": 40
    }

    parametersLarge = {
        "candidate_count": 1,
        "max_output_tokens": 4096,
        "temperature": 0.1,
        "top_p": 0.8,
        "top_k": 40
    }



    model = TextGenerationModel.from_pretrained(CONFIG.vertex_model)
    modelLarge= TextGenerationModel.from_pretrained(CONFIG.vertex_model_large)

    system_prompt = 'You are a helpful assistant.'




    def _user_msg(self, msg: str) -> dict[str, str]:
        return msg

    def _system_msg(self, msg: str) -> dict[str, str]:
        return msg
    def _system_msgs(self, msgs: list[str]) -> list[dict[str, str]]:
        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self):
        return self._system_msg(self.system_prompt)

    def ask(self, prompt):

        result = self.model.predict(prompt, **self.parameters)

        return result.text

    async def aask(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        if system_msgs:
            message = str(self._system_msgs(system_msgs) + [self._user_msg(msg)])
        else:
            message = self._default_system_msg() + self._user_msg(msg)
        result = self.model.predict(msg, **self.parameters)


        logger.info(message)
        logger.info(result.text)
        return result.text


    async def aasklarge(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        if system_msgs:
            message = str(self._system_msgs(system_msgs) + [self._user_msg(msg)])
        else:
            message = self._default_system_msg() + self._user_msg(msg)
        result = self.modelLarge.predict(msg, **self.parametersLarge)


        logger.info(message)
        logger.info(result.text)
        return result.text

    async def aaskes(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        logger.info ("Invoking Research Agent :" + CONFIG.es_store_project)
        GCP_PROJECT = CONFIG.es_store_project  # @param {type: "string"}
        SEARCH_ENGINE = CONFIG.es_store  # @param {type: "string"}
        LLM_MODEL = "text-bison@latest"  # @param {type: "string"}
        MAX_OUTPUT_TOKENS = 1024  # @param {type: "integer"}
        TEMPERATURE = 0.0  # @param {type: "number"}
        TOP_P = 0.8  # @param {type: "number"}
        TOP_K = 40  # @param {type: "number"}
        VERBOSE = True  # @param {type: "boolean"}
        llm_params = dict(
            model_name=LLM_MODEL,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            verbose=VERBOSE,
        )

        retriever = GoogleVertexAISearchRetriever(
            project_id=GCP_PROJECT,
            location_id="us",
            data_store_id=SEARCH_ENGINE,
            max_documents=3,
            max_extractive_answer_count=5,
            get_extractive_answers=True,
            engine_data_type=0,

        )

        results = retriever.get_relevant_documents(msg)
        for doc in results:
            logger.info(doc.page_content + "   " + doc.metadata['source'])


        msg = f"Summarize the page_content based on the relevance related to Question: {msg} from the context \n Context: \n Ignore non relevant text" + str(results) + "\n Summarize as Bullets with Source Information Answer:"
        print(msg)
        result = self.model.predict(msg, **self.parameters)

        if system_msgs:
            message = str(self._system_msgs(system_msgs))
        else:
            message = self._default_system_msg()

        # prompt = PromptTemplate(input_variables=['results'],
        #                         template=message)



        return str(result.text)



    async def aasklargegemini(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        PROJECT_ID = CONFIG.vertex_special_project  # @param
        LOCATION = CONFIG.vertex_location  # @param
        vertexai.init(project=PROJECT_ID, location=LOCATION)

        modelgemini=GenerativeModel(CONFIG.vertex_model_mm)
        if system_msgs:
            message = str(self._system_msgs(system_msgs)) + " \n " + str([self._user_msg(msg)])
        else:
            message = self._default_system_msg() + " \n " + self._user_msg(msg)
        result = modelgemini.generate_content(msg, generation_config={
        "temperature": 0.01,
        "top_p": 0.85,
        "top_k": 20,
        "candidate_count": 1,
        "max_output_tokens": 2000,
        "stop_sequences": ["STOP!"],
    })

        logger.info(message)
        logger.info(result.candidates[0].content.parts[0].text)
        return str(result.candidates[0].content.parts[0].text)

    async def aasklargegeminimm(self, msg: str, img: str) -> str:
            PROJECT_ID = CONFIG.vertex_special_project  # @param
            LOCATION = CONFIG.vertex_location  # @param
            vertexai.init(project=PROJECT_ID, location=LOCATION)

            with open(img, "rb") as image_file:
                image_data = image_file.read()

            encoded_image = base64.b64encode(image_data).decode("utf-8")

            multimodal_model = GenerativeModel(CONFIG.vertex_model_mmv)

            image = generative_models.Part.from_data(data=base64.b64decode(encoded_image), mime_type="image/png")

            responses = multimodal_model.generate_content([msg, image])

            print(responses.text)

            return responses.text




