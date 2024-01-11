#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/19 08:04
@Author  : asanthan
@File    : product_idea_researcher.py
"""
from metagpt.actions import WriteTasks
from metagpt.actions.cpg_product_research import ConductResearch
from metagpt.actions.design_api import WriteDesign
from metagpt.actions.generate_product_concepts import GenerateProductConcepts
from metagpt.roles import Role


class ProductResearcher(Role):
    """
    Represents a Sr Product Researcher responislbe for overseeing and launching new product ideas for the CPG company .

    Attributes:
        name (str): Name of the Product Researcher.
        profile (str): Role profile, default is 'Sr Product Researcher'.
        goal (str): Goal of the project researcher.
        constraints (str): Constraints or limitations for the product researcher.
    """

    def __init__(
        self,
        name: str = "Eve",
        profile: str = "Project Researcher",
        goal: str = "Generated 5 solid Product Concept development ideas",
        constraints: str = "",
    ) -> None:
        """
        Initializes the Product Researcher role with given attributes.

        Args:
            name (str): Name of the Product Researcher.
            profile (str): Role profile, default is 'Sr Product Researcher'.
            goal (str): Goal of the project researcher.
            constraints (str): Constraints or limitations for the product researcher.
        """
        super().__init__(name, profile, goal, constraints)
        self._init_actions([GenerateProductConcepts])
        self._watch([ConductResearch])
