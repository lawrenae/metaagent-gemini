#!/usr/bin/env python

"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : cpg_product_review_research.py
"""

from __future__ import annotations

import asyncio
import json
import os
from asyncio import sleep
from typing import Callable

from pydantic import parse_obj_as

from metagpt.actions import Action
from metagpt.config import CONFIG
from metagpt.const import DATA_PATH
from metagpt.logs import logger
from metagpt.tools.search_engine import SearchEngine
from metagpt.tools.web_browser_engine import WebBrowserEngine, WebBrowserEngineType
from metagpt.utils.common import OutputParser
from metagpt.utils.text import generate_prompt_chunk, reduce_message_length

LANG_PROMPT = "Please respond in {language}."

RESEARCH_BASE_SYSTEM = """You are an AI critical thinker research assistant. Your sole purpose is to write well \
written, critically acclaimed, objective and structured reports on the given text."""

RESEARCH_TOPIC_SYSTEM = "You are an AI researcher assistant for CPG industry conducting market research, and your research topic is:\n#TOPIC#\n{topic}"

SEARCH_TOPIC_PROMPT = """Please provide up to 2 necessary keywords related to your research {topic} for Google search. \
Your response must be in JSON format, for example: ["keyword1", "keyword2"]."""

GENERATE_RESEARCH_QUERY_PROMPT = """### Requirements

You are a AI research assistant helping Product Researcher in CPG Product Innovation Study to create a Executive Summary of New Product Research Study

1. Your task is to generate questions needed for conducting the {topic} Study using VertexAI search related to various areas listed in research area section below
2. Provide up to {decomposition_nums} queries per sections listed in research area  below.
3. Please respond in the following array format, for example [["section1" , "query1"], ["section1" , "query2"],["section2" , "query1"], ...].

### Research Area
{research_areas}
"""

GENERATE_PRODUCT_IDEAS_PROMPT = """
You are a world renowned CPG Product Researcher AI Agent . Please leverage the research content below and based on the factual evidence presented below , 
generate top 5 ideas for {topic} product . The section should include tag line of the idea needed for marketing, a brief description of the idea and should include facts from the research to derive the reason to believe for the idea , market opportunity for this idea including demographics and user segmentation. 
The idea should directly address the key concerns reported as part of the research study and also focus on marketing and technology trends and opportunities .
Report must be in the markdown format

### Reference Information

{content}


"""


ENTERPRISE_SEARCH_AND_SUMMARIZE_PROMPT = '''### Requirements
1. Let's think step by step in answering the question by applying relevance to the query being asked.
2. Please search for the following topic "{query}".
'''


CONDUCT_RESEARCH_PROMPT = '''
### Requirements
You are a AI research assistant helping Product Researcher in CPG Product Innovation Study to create a Executive Summary of New Product Research Study , Only answer from the provided context. 

Step 1: Let's think Step by Step in providing a detailed research report researching for new Product Idea using the information provided in the  ### Reference Information below .The report must meet the following requirements:
Step 2: Elaborate the key topics mentioned in Reference Section and generate a  report up to 4000 words into minimum of 5 bullets using Markdown Syntax
Step 3: The Report must include  following sections. Title as Research Topic, Executive Summary , Subsections listed in the ### Reference Information section.
Step 4: Gather the Source information from ### Reference Information and convert it into hyperlink and Summarize it in the Citation section using the markdown format.
Step 5: Remove duplicate entries from Source Citations sections


### Reference Information
{content}


'''



class GenerateResearchQueries(Action):
    """Action class to collect links from a search engine."""
    def __init__(
        self,
        name: str = "",
        *args,
        **kwargs,
    ):
        super().__init__(name, *args, **kwargs)
        self.desc = "Generate Queries for Research."


    async def run(
        self,
        topic: str,
        decomposition_nums: int = 5,
        topic_research_area: list[str] | None = None,
        system_text: str | None = None,
    ) -> dict[str, list[str]]:
        """Run the action to collect links.

        Args:
            topic: The research topic.
            decomposition_nums: The number of search questions to generate.
            topic_research_area: Key Sections needed for the Research Study Report.
            system_text: The system text.

        Returns:
            A dictionary containing the search questions as keys and the collected URLs as values.
        """
        system_text = system_text if system_text else RESEARCH_TOPIC_SYSTEM.format(topic=topic)
        queries = self._aask(GENERATE_RESEARCH_QUERY_PROMPT.format(topic=topic,decomposition_nums=decomposition_nums, research_areas=topic_research_area), [system_text])
        try:
            questions = OutputParser.extract_struct(queries, list)
            questionsDic = {}
            for row in questions:
                key, value = row
                if key not in questionsDic:
                    questionsDic[key] = []
                questionsDic[key].append(value)

            # Print the dictionary
            print(questionsDic)
            #questions = parse_obj_as(list[str,str], questions)
        except Exception as e:
            logger.exception(f"fail to get keywords related to the research topic \"{topic}\" for {e}")
            keywords = [topic]
        results = questionsDic
        #print(results)

        return results






class VertexSearchAndSummarize(Action):
    """Action class to explore the web and provide summaries of articles and webpages."""
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # if CONFIG.model_for_researcher_summary:
        #     self.llm.model = CONFIG.model_for_researcher_summary
        self.desc = "Search the Knowledge Base Stored in Vertex AI Enterprise Search."

    async def run(
        self,
        section: str,
        query: list[str],
        system_text: str = RESEARCH_BASE_SYSTEM,
    ) -> dict[str, dict[str,str]]:
        """Run the action to browse the web and provide summaries.

        Args:
            section: key section for the research topic
            query: list of The research questions for the section.
            system_text: The system text.

        Returns:
            A dictionary containing the key Section as keys and their questions and summaries as list of values.
        """

        summaries = {}
        content = {}

        for q in query:
            print(f"""Processing {q}""")
            prompt = ENTERPRISE_SEARCH_AND_SUMMARIZE_PROMPT.format(query=q)
            summary = await self._aaskes(prompt, [])
            key = q
            if key not in content:
                content[key] = []
            content[key].append(summary)
            #content[q].append(summary)
        summaries[section]=content
        return summaries


class ConductResearch(Action):
    """Action class to conduct research and generate a research report."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if CONFIG.model_for_researcher_report:
        #     self.llm.model = CONFIG.model_for_researcher_report

    async def run(
        self,
        topic: str,
        content: str,
        system_text: str = RESEARCH_BASE_SYSTEM,
    ) -> str:
        """Run the action to conduct research and generate a research report.

        Args:
            topic: The research topic.
            content: The content for research.
            system_text: The system text.

        Returns:
            The generated research report.
        """
        logger.info("**********************")
        logger.info(content)
        logger.info("**********************")
        prompt = CONDUCT_RESEARCH_PROMPT.format(topic=topic, content=content)
        logger.debug(prompt)
        contents = await self._aaskl(prompt, [])
        logger.info(contents)
        maincontent = "\n\n ## Market Forecast \n\n"
        for root, _, files in os.walk(DATA_PATH/"charts"):
            for filename in files:
                if filename.endswith(".png"):

                    title = await self._aaskml("All these chart represent data on Sunscreen , What is the title for this chart ?",
                                                      DATA_PATH/"charts"/filename)
                    imgcontent = f" ### {title} \n\n ![{title}](../charts/{filename})"
                    logger.info(imgcontent)
                    chartcontent = await self._aaskml("All these chart represent data on Sunscreen , Summarize 3 key inference as bullets from the Chart", DATA_PATH / "charts" / filename )
                    logger.info(chartcontent)
                    maincontent = maincontent+"\n\n"+ imgcontent + " \n\n ### Summary\n" + chartcontent+"\n\n"



        logger.info(maincontent)

        contents = contents + "\n \n" + maincontent
        return contents


class GenerateProductConcepts(Action):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if CONFIG.model_for_researcher_report:
        #     self.llm.model = CONFIG.model_for_researcher_report

    async def run(
        self,
        topic: str,
        content: str,
        system_text: str = RESEARCH_BASE_SYSTEM,
    ) -> str:
        """Run the action to generate top 5 product ideas based on the research and generate concept development document.

        Args:
            topic: The research topic.
            content: The content from research.
            system_text: The system text.

        Returns:
            The generated research report.
        """
        logger.info("**********************")
        logger.info(content)
        logger.info("**********************")
        prompt = GENERATE_PRODUCT_IDEAS_PROMPT.format(topic=topic, content=content)
        logger.debug(prompt)
        contents = await self._aaskl(prompt, [])
        logger.info(contents)

        return contents


def get_research_system_text(topic: str, language: str):
    """Get the system text for conducting research.

    Args:
        topic: The research topic.
        language: The language for the system text.

    Returns:
        The system text for conducting research.
    """
    return " ".join((RESEARCH_TOPIC_SYSTEM.format(topic=topic), LANG_PROMPT.format(language=language)))
