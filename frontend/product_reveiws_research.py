#!/usr/bin/env python

import asyncio

from metagpt.roles.cpg_product_reviewe_researcher import RESEARCH_PATH, Researcher


async def main():
    topic = "Sunscreen Product Reviews"
    role = Researcher(language="en-us")
    await role.run(topic)
    print(f"save report to {RESEARCH_PATH / f'{topic}.md'}.")


if __name__ == '__main__':
    asyncio.run(main())
