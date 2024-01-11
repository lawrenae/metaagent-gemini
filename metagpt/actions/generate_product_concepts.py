#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/19 08:04
@Author  : asanthan
@File    : generate_product_concepts.py
"""
from typing import List

from metagpt.actions import Action, ActionOutput
from metagpt.actions.search_and_summarize import SearchAndSummarize
from metagpt.config import CONFIG
from metagpt.const import RESEARCH_PATH
from metagpt.logs import logger
from metagpt.utils.get_template import get_template

RESEARCH_BASE_SYSTEM = """You are an AI critical thinker research assistant. Your sole purpose is to write well \
written, critically acclaimed, objective and structured reports on the given text."""


GENERATE_PRODUCT_IDEAS_PROMPT = """
You are a world renowned CPG Product Researcher AI Agent . Please leverage the research content below and based on the factual evidence presented below , 
generate top 5 ideas for {topic} product . The section should include tag line of the idea needed for marketing, a brief description of the idea and should include facts from the research to derive the reason to believe for the idea , market opportunity for this idea including demographics and user segmentation. 
The idea should directly address the key concerns reported as part of the research study and also focus on marketing and technology trends and opportunities .

### Reference Information

{content}


"""


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
        self.write_report(topic, contents)

        return contents


    def write_report(self, topic: str, content: str):
        if not RESEARCH_PATH.exists():
            RESEARCH_PATH.mkdir(parents=True)
        filepath = RESEARCH_PATH / f"{topic}_Concept_Document.md"
        filepath.write_text(content)