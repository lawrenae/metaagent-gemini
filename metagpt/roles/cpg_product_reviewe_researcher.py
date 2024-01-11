#!/usr/bin/env python

"""
@Time    : 2023/12/03 14:58
@Author  : asanthan
@File    : cpg_product_review_researcher.py
"""

import asyncio

from pydantic import BaseModel
from metagpt.actions.cpg_product_research import VertexSearchAndSummarize, ConductResearch, GenerateResearchQueries, \
    get_research_system_text
from metagpt.actions.cpg_product_review_research import DownloadReviews, ExtractReviewTopic_Sentiment, \
    ConsolidateReviewsStudy
from metagpt.const import RESEARCH_PATH
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message


class Report(BaseModel):
    topic: str
    raw_reviews: str = None
    processed_reviews: dict[str, list[str]] = None
    summaries: dict[str, dict[str, list[str]]] = None
    content: str = ""


class Researcher(Role):
    def __init__(
            self,
            name: str = "Reviews_Minion",
            profile: str = "Product Reviews Research Analyst",
            goal: str = "Gather information and conduct research on CPG related Product Reviews Research",
            constraints: str = "Ensure accuracy and relevance of information",
            language: str = "en-us",
            **kwargs,
    ):
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions([DownloadReviews(name), ExtractReviewTopic_Sentiment(name)])
        self.language = language
        if language not in ("en-us", "zh-cn"):
            logger.warning(f"The language `{language}` has not been tested, it may not work.")

    async def _think(self) -> None:
        if self._rc.todo is None:
            self._set_state(0)
            return

        if self._rc.state + 1 < len(self._states):
            self._set_state(self._rc.state + 1)
        else:
            self._rc.todo = None

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        todo = self._rc.todo
        msg = self._rc.memory.get(k=1)[0]
        if isinstance(msg.instruct_content, Report):
            instruct_content = msg.instruct_content
            topic = instruct_content.topic
        else:
            topic = msg.content
        instruct_content = msg.instruct_content
        research_system_text = get_research_system_text(topic, self.language)

        if isinstance(todo, DownloadReviews):
            urls = [

                "https://www.amazon.com/Neutrogena-Ultra-Dry-Touch-Sunscreen-Spectrum/product-reviews/B005IHT94S/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
                "https://www.amazon.com/Neutrogena-Ultra-Dry-Touch-Sunscreen-Spectrum/product-reviews/B005IHT94S/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2",
                "https://www.amazon.com/Neutrogena-Ultra-Dry-Touch-Sunscreen-Spectrum/product-reviews/B005IHT94S/ref=cm_cr_arp_d_paging_btm_next_3?ie=UTF8&reviewerType=all_reviews&pageNumber=3",
                "https://www.amazon.com/Pipette-Sunscreen-Spectrum-Non-nano-4-Fluid-Ounce/product-reviews/B085Z49QW6/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews",
                "https://www.amazon.com/Pipette-Sunscreen-Spectrum-Non-nano-4-Fluid-Ounce/product-reviews/B085Z49QW6/ref=cm_cr_arp_d_paging_btm_next_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2",
                "https://www.amazon.com/Pipette-Sunscreen-Spectrum-Non-nano-4-Fluid-Ounce/product-reviews/B085Z49QW6/ref=cm_cr_arp_d_paging_btm_next_3?ie=UTF8&reviewerType=all_reviews&pageNumber=3",

            ]
            links = await todo.run(urls)
            ret = Message("", Report(topic=topic, raw_reviews=links), role=self.profile, cause_by=type(todo))
            print(ret)
        elif isinstance(todo, ExtractReviewTopic_Sentiment):
            links = instruct_content.raw_reviews
            todos = todo.run(reviews=links, system_text=research_system_text)
            reviews = await todos
            # summaries = await(todos)
            logger.info(todos)
            # summaries = dict((section, summary) for i in summaries for (section, summary) in i.items() if summary)
            # ret = Message("", Report(topic=topic, summaries=summaries), role=self.profile, cause_by=type(todo))
            # print(ret)
        else:
            summaries = instruct_content.summaries
            # summary_text = "\n---\n".join(f"topic: {section}\nsummary: {summary}" for section, summary in summaries)
            print("********Inside Research")
            print(summaries)
            summary_texts = []
            for section, sub_dict in summaries.items():
                summary_text = f"## Section: {section}\n\n"
                for question, content in sub_dict.items():
                    summary_text += f"\n### Question: {question}\n\n"
                    for item in content:
                        summary_text += f"- {item}\n"
                summary_texts.append(summary_text)
            summary_text = "\n---\n".join(summary for summary in summary_texts)
            print(summary_text)
            content = await self._rc.todo.run(topic, summary_text, system_text=research_system_text)
            ret = Message("", Report(topic=topic, content=content), role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(ret)
        return ret

    async def _react(self) -> Message:
        while True:
            await self._think()
            if self._rc.todo is None:
                break
            msg = await self._act()
        report = msg.instruct_content
        self.write_report(report.topic, report.content)
        return msg

    def write_report(self, topic: str, content: str):
        if not RESEARCH_PATH.exists():
            RESEARCH_PATH.mkdir(parents=True)
        filepath = RESEARCH_PATH / f"{topic}.md"
        filepath.write_text(content)


if __name__ == "__main__":
    import fire


    async def main(topic: str, language="en-us"):
        role = Researcher(topic, language=language)
        await role.run(topic)


    fire.Fire(main)
