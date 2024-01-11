#!/usr/bin/env python

"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : cpg_product_research.py
"""

from __future__ import annotations

import asyncio
import json
from typing import Callable
from pydantic import parse_obj_as
from metagpt.const import REVIEWS_PATH
from metagpt.actions import Action
from metagpt.config import CONFIG
from metagpt.logs import logger
from metagpt.tools.search_engine import SearchEngine
from metagpt.tools.web_browser_engine import WebBrowserEngine, WebBrowserEngineType
from metagpt.utils.common import OutputParser
from metagpt.utils.text import generate_prompt_chunk, reduce_message_length

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import logging

headers = {
    "authority": "www.amazon.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "document",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
}


def get_page_html(page_url: str) -> str:
    resp = requests.get(page_url, headers=headers)
    return resp.text


def get_reviews_from_html(page_html: str) -> BeautifulSoup:
    soup = BeautifulSoup(page_html, "lxml")
    reviews = soup.find_all("div", {"class": "a-section celwidget"})
    return reviews


def get_review_date(soup_object: BeautifulSoup):
    date_string = soup_object.find("span", {"class": "review-date"}).get_text()
    return date_string


def get_review_text(soup_object: BeautifulSoup) -> str:
    review_text = soup_object.find(
        "span", {"class": "a-size-base review-text review-text-content"}
    ).get_text()
    return review_text.strip()


def get_review_header(soup_object: BeautifulSoup) -> str:
    review_header = soup_object.find(
        "a",
        {
            "class": "a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold"
        },
    ).get_text()
    return review_header.strip()


def get_number_stars(soup_object: BeautifulSoup) -> str:
    stars = soup_object.find("span", {"class": "a-icon-alt"}).get_text()
    return stars.strip()


def get_product_name(soup_object: BeautifulSoup) -> str:
    product = soup_object.find(
        "a", {"class": "a-size-mini a-link-normal a-color-secondary"}
    ).get_text()
    return product.strip()


def orchestrate_data_gathering(single_review: BeautifulSoup) -> dict:
    return {
        "review_text": get_review_text(single_review),
        "review_date": get_review_date(single_review),
        "review_title": get_review_header(single_review),
        "review_stars": get_number_stars(single_review),
        "review_flavor": get_product_name(single_review),
    }

LANG_PROMPT = "Please respond in {language}."

RESEARCH_BASE_SYSTEM = """You are an AI critical thinker research assistant. Your sole purpose is to write well \
written, critically acclaimed, objective and structured reports on the given text."""

REVIEWS_CLASSIFIER_PROMPT = """### Requirements

1. Below is a set of customer reviews delimited with {delimiter}.

2. Evaluate the Customer Review

3. Classify the review category based on the following list of category like  Whitecast , Greasiness , Pricing , Effectiveness , Packaging

4. From the review , identify up to top 2 features customer is happy and not happy with the product .

5. Return only  top 5 list  based on the sentiment severity of the review category of the customer reviews. Ignore the category not mentioned in the reviews. Ignore category with null review_text

Customer reviews:
{delimiter}
{reviews}
{delimiter}
"""

REVIEWS_CLASSIFIER_PROMPT_OUT = """Output is a JSON list as string with the following format
[
{"product_name" : "<product_name>","product_sub_category": "SPF30" , "review_category": "<category1> , <category2>", "review_text": "<full_review_text>" , "topic_sentiment" : "<topic1_sentiment>"},
{"product_name" : "<product_name>","product_sub_category": "SPF45","review_category": "<category1> , <category2>", "review_text": "<full_review_text>", "topic_sentiment" : "<topic2_sentiment>"},
...
]

"""

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


ENTERPRISE_SEARCH_AND_SUMMARIZE_PROMPT = '''### Requirements
1. Please search for the following topic "{query}".
'''


CONDUCT_RESEARCH_PROMPT = '''### Reference Information
{content}

### Requirements
You are a AI research assistant helping Product Researcher in CPG Product Innovation Study to create a Executive Summary of New Product Research Study , Only answer from the provided context. Do not hallucinate

### Requirements
Step 1: Please provide a detailed research report using the information provided in the  Reference Information  section below . The report must meet the following requirements:
Step 2: The  Reference Information  section specifics topics under url: , content under summary  , citation under summary
Step 3: Elaborate the key topics mentioned in Reference Section and generate a  report up to 5000 words into minimum of 5 bullets using Markdown Syntax
Step 4: The Report must include  following sections. Title as Research Topic, Executive Summary , Subsections  Core functions, ideal product/service/experience, consumer satisfaction, current gaps, market trends and opportunities, and key technology and scientific advancements in sunscreen , Source Citations
Step 5: Remove duplicate entries from Source Citations sections
'''



class DownloadReviews(Action):
    """Action class to collect links from a search engine."""
    def __init__(
        self,
        name: str = "",
        *args,
        **kwargs,
    ):
        super().__init__(name, *args, **kwargs)
        self.desc = "Download sample reviews for Review Analyzer Bot."



    async def run(
        self,
        urls: list[str],
        system_text: str | None = None,
    ) -> str:
        """Run the action to collect links.

        Args:
            urls: Amazon reviews.
            system_text: The system text.

        Returns:
            A dictionary containing the search questions as keys and the collected URLs as values.
        """
        try:

            all_results = []
            save_name = ""
            logger.info(urls)
            for u in urls:
                logging.info(u)
                html = get_page_html(u)
                reviews = get_reviews_from_html(html)
                for rev in reviews:
                    data = orchestrate_data_gathering(rev)
                    all_results.append(data)

            out = pd.DataFrame.from_records(all_results)
            if (out.empty):
                logging.info('Nothing Retrieved')

            else:
                logging.info(f"{out.shape[0]} Is the shape of the dataframe")
                save_name = REVIEWS_PATH/ f"{datetime.now().strftime('%Y-%m-%d-%m')}.csv"
                logging.info(f"saving to {save_name}")
                out.to_csv(save_name)



        except Exception as e:
            logger.exception(f"fail to get download reviews related to the research topic \"{u}\" for {e}")
        return "/Users/asanthan/work/development/llm/MetaGemini/data/reviews/2023-11-05-11.csv"
        #return str(REVIEWS_PATH/+ f"{datetime.now().strftime('%Y-%m-%d-%m')}.csv")
        #print(results)








class ExtractReviewTopic_Sentiment(Action):
    """Action class to explore the web and provide summaries of articles and webpages."""
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # if CONFIG.model_for_researcher_summary:
        #     self.llm.model = CONFIG.model_for_researcher_summary
        self.desc = "Process Each Reviews and Cluster by key Review Topic and Access the Sentiment"

    async def run(
        self,
        reviews: str,
        system_text: str = RESEARCH_BASE_SYSTEM,
    ) -> dict[str, dict[str,str]]:
        """Run the action to browse the web and provide summaries.

        Args:
            reviews: location of the downloaded reviews
            query: list of The research questions for the section.
            system_text: The system text.

        Returns:
            A dictionary containing the key Section as keys and their questions and summaries as list of values.
        """

        processedreviews = {}

        df = pd.read_csv(REVIEWS_PATH / f"2023-11-05-11.csv")
        logger.info(df.head(2))
        delimiter = "###"
        for index, row in df.iterrows():
            review = row['review_text']
            print(f"""Processing {review}""")
            prompt = REVIEWS_CLASSIFIER_PROMPT.format(delimiter=delimiter,reviews=review)
            prompt = prompt + REVIEWS_CLASSIFIER_PROMPT_OUT
            summary = await self._aask(prompt, [])
            review_processed =  json.loads(summary)
            print(review_processed)
            processedreviews[review_processed[0]['product_name']]=review_processed

        return processedreviews


class ConsolidateReviewsStudy(Action):
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
        self.llm.auto_max_tokens = True
        content = await self._aaskl(prompt, [system_text])
        return content


def get_research_system_text(topic: str, language: str):
    """Get the system text for conducting research.

    Args:
        topic: The research topic.
        language: The language for the system text.

    Returns:
        The system text for conducting research.
    """
    return " ".join((RESEARCH_TOPIC_SYSTEM.format(topic=topic), LANG_PROMPT.format(language=language)))
