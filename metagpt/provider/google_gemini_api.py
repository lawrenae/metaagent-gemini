"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : google_palm_api.py
"""


import asyncio
import time
from typing import Optional
import vertexai
import vertexai.generative_models as generative_models
from vertexai.generative_models import GenerativeModel, Part
from typing import Optional
from metagpt.config import CONFIG
from metagpt.logs import logger

from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains import LLMChain
from langchain.retrievers import (
    GoogleVertexAISearchRetriever,
)
from typing import Any, List, Dict, Optional


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

class Gemini:
    system_prompt = 'You are a helpful assistant.'

    def __init__(self) -> None:
        PROJECT_ID = CONFIG.vertex_project  # @param
        LOCATION = CONFIG.vertex_location  # @param
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        self.model = GenerativeModel(CONFIG.vertex_model_gemini)

    def _user_msg(self, msg: str) -> dict[str, str]:
        return msg

    def _system_msg(self, msg: str) -> dict[str, str]:
        return msg

    def _system_msgs(self, msgs: list[str]) -> list[dict[str, str]]:
        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self):
        return self._system_msg(self.system_prompt)

    def ask(self, prompt):
        result = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 8192,
                "temperature": 0.9,
                "top_p": 1
            },
            safety_settings={
                  generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                  generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                  generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                  generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            },
            stream=False,
        )

        logger.info(prompt)
        logger.info(result.text)
        return result.text

    def aask(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        return self._aask(msg, system_msgs)

    def _aask(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        if system_msgs:
            message = str(self._system_msgs(system_msgs) + [self._user_msg(msg)])
        else:
            message = self._default_system_msg() + self._user_msg(msg)

        return self.ask(message)

    async def aaskes(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        logger.info ("Invoking Research Agent :" + CONFIG.vertex_project)
        GCP_PROJECT = CONFIG.vertex_project  # @param {type: "string"}
        SEARCH_ENGINE = CONFIG.es_store  # @param {type: "string"}
        LLM_MODEL = CONFIG.vertex_model_gemini  # @param {type: "string"}
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

        result = self.model.generate_content(msg, generation_config={
                "temperature": 0.01,
                "top_p": 0.85,
                "top_k": 20,
                "candidate_count": 1,
                "max_output_tokens": 2000,
                "stop_sequences": ["STOP!"],
            })


        # if system_msgs:
        #     message = str(self._system_msgs(system_msgs))
        # else:
        #     message = self._default_system_msg()

        # prompt = PromptTemplate(input_variables=['results'],
        #                         template=message)



        return str(result.text)



    async def aasklargegemini(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        if system_msgs:
            message = str(self._system_msgs(system_msgs)) + " \n " + str([self._user_msg(msg)])
        else:
            message = self._default_system_msg() + " \n " + self._user_msg(msg)
        result = self.model.generate_content(msg, generation_config={
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
        with open(img, "rb") as image_file:
            image_data = image_file.read()

        # encoded_image = base64.b64encode(image_data).decode("utf-8")
        # image = Part.from_data(data=base64.b64decode(encoded_image), mime_type="image/png")
        image = Part.from_data(data=image_data, mime_type="image/png")

        responses = self.model.generate_content([msg, image])

        print(responses.text)

        return responses.text