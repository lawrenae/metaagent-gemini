#!/usr/bin/env python

"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : cpg_product_researcher.py
"""

import asyncio

from pydantic import BaseModel
from metagpt.actions.cpg_product_research import VertexSearchAndSummarize, ConductResearch, GenerateResearchQueries, \
    get_research_system_text, GenerateProductConcepts
from metagpt.config import CONFIG
from metagpt.const import RESEARCH_PATH
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message


class Report(BaseModel):
    topic: str
    links: dict[str, list[str]] = None
    summaries: dict[str, dict[str, list[str]]] = None
    content: str = ""


class Researcher(Role):
    def __init__(
            self,
            name: str = "Arun's Research Minion",
            profile: str = "Product Research Analyst",
            goal: str = "Gather information and conduct research on CPG related Market Research",
            constraints: str = "Ensure accuracy and relevance of information",
            language: str = "en-us",
            **kwargs,
    ):
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions([GenerateResearchQueries(name), VertexSearchAndSummarize(name), ConductResearch(name),GenerateProductConcepts(name)])
        self.language = language
        if language not in ("en-us", "zh-cn"):
            logger.warning(f"The language `{language}` has not been tested, it may not work.")

    def create_summary_text(data):
        """
        Creates a summary text for each topic and its respective question and content.

        Args:
            data: A dictionary containing topics as keys and sub-dictionaries as values.
                The sub-dictionaries contain questions as keys and lists of content as values.

        Returns:
            A list of strings, each representing the summary text for a topic.
        """

        summary_texts = []
        for topic, sub_dict in data.items():
            summary_text = f"## Topic: {topic}\n\n"
            for question, content in sub_dict.items():
                summary_text += f"\n### Question: {question}\n\n"
                for item in content:
                    summary_text += f"- {item}\n"
            summary_texts.append(summary_text)
        return summary_texts
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

        if isinstance(todo, GenerateResearchQueries):
            # subsections = ['Core functions', 'ideal product/service/experience', 'consumer satisfaction',
            #                'current gaps', 'market trends', 'key technology and scientific advancements']
            subsections = CONFIG.gen_research_subsection
            links = await todo.run(topic, CONFIG.gen_research_questions, subsections)
            ret = Message("", Report(topic=topic, links=links), role=self.profile, cause_by=type(todo))
            print(ret)
        elif isinstance(todo, VertexSearchAndSummarize):
            links = instruct_content.links
            # queries = ["What are the core functions of sunscreen?",
            #            "What is the ideal product experience for sunscreen?",
            #            "What are the current market trends in terms of market potential and consumer needs for sunscreen?",
            #            "What are the current gaps in the sunscreen market? ",
            #            "What are the key technologies and research advancements?",
            #            "What are the regulatory requirements for sunscreen products?",
            #            "What are the safety and efficacy concerns associated with sunscreen products?",
            #            "What are the consumer preferences and attitudes towards sunscreen products?",
            #            "What are the pricing and distribution strategies for sunscreen products?",
            #            "What are the marketing and promotional strategies for sunscreen products?"]

            # todos = todo.run(query=links, system_text=research_system_text) for query in queries)

            todos = (todo.run(section=section, query=query, system_text=research_system_text) for (section, query) in
                     links.items())
            summaries = await asyncio.gather(*todos)
            # summaries = await(todos)
            logger.info(summaries)
            summaries = dict((section, summary) for i in summaries for (section, summary) in i.items() if summary)
            ret = Message("", Report(topic=topic, summaries=summaries), role=self.profile, cause_by=type(todo))

            print(ret)
        elif isinstance(todo, ConductResearch):
            summaries = instruct_content.summaries
            # summary_text = "\n---\n".join(f"topic: {section}\nsummary: {summary}" for section, summary in summaries)
            print("********Inside Research")
            print(summaries)
            summary_texts=[]
            for section, sub_dict in summaries.items():
                summary_text = f"## Section: {section}\n\n"
                for question, content in sub_dict.items():
                    summary_text += f"\n### Question: {question}\n\n"
                    for item in content:
                        summary_text += f"- {item}\n"
                summary_texts.append(summary_text)
            summary_text = "\n---\n".join(summary for summary in summary_texts)
            print(summary_text)
            self.write_report(topic+" QnA", summary_text)
            content = await self._rc.todo.run(topic, summary_text, system_text=research_system_text)
            ret = Message("", Report(topic=topic, content=content), role=self.profile, cause_by=type(self._rc.todo))
        else :
            content = instruct_content.content
            self.write_report(topic + "_Dossier", content)
            content = await self._rc.todo.run(topic, content, system_text=research_system_text)
            ret = Message("", Report(topic=topic+"_ConceptDevelopment", content=content), role=self.profile, cause_by=type(self._rc.todo))

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
