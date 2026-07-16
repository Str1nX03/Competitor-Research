from typing import TypedDict, List, Dict
from src.utils import get_llm, web_search
from langchain_core.prompts import ChatPromptTemplate
from src.exception import CustomException
import sys
import json
from langgraph.graph import StateGraph, START, END
from src.prompts.researcher_prompt import COMPETITOR_EXTRACT_PROMPT

class AgentState(TypedDict):

    user_input: str
    competitors: List[str]
    research_data: Dict[str, List[str]]

class ResearcherAgent:

    def __init__(self):
        
        self.llm = get_llm()
        self.graph = self._build_graph()

    def _extract_competitor(self, state: AgentState):

        try:

            competitor_data = []
            user_input = state["user_input"]

            query = f"Who are the competitors of {user_input}"

            competitor_data = web_search(query)

            schema = {
                "title": "CompetitorExtraction",
                "type": "object",
                "properties": {
                    "competitors": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of competitors names extracted from the query"
                    }
                },
                "required": ["competitors"]
            }

            structured_llm = self.llm.with_structured_output(schema, method="json_mode")

            prompt = ChatPromptTemplate.from_template(COMPETITOR_EXTRACT_PROMPT)

            response = structured_llm.invoke(prompt.format(
                competitor_data = competitor_data
            ))

            competitors = response.get("competitors", []) if isinstance(response, dict) else []

            return {"competitors": competitors}

        except Exception as e:

            raise CustomException(e,sys)

    def _research_competitor_data(self, state: AgentState):
        try:
            
            competitors = state["competitors"]
            questions = [
                "Website URL (if it is a company)",
                "What is the product",
                "What is the revenue and profit they generate",
                "What does the product/company do",
                "What is the pricing (monthly/yearly)"
            ]

            research_data = {}

            for competitor in competitors:

                research_data[competitor] = []
                
                for question in questions:
                    
                    search_results = web_search(query = question + " of " + competitor + "?", max_results = 1)

                    research_data[competitor].append(search_results)

            return {"research_data": research_data}

        except Exception as e:
            raise CustomException(e,sys)

    def _build_graph(self):

        try:

            graph = StateGraph(AgentState)

            graph.add_node("extract_competitor", self._extract_competitor)
            graph.add_node("research_competitor_data", self._research_competitor_data)

            graph.add_edge(START, "extract_competitor")
            graph.add_edge("extract_competitor", "research_competitor_data")
            graph.add_edge("research_competitor_data", END)

            return graph.compile()

        except Exception as e:

            raise CustomException(e,sys)

    def run(self, user_input: str):

        try:

            initial_state = {
                "user_input": user_input,
                "competitors": [],
                "research_data": {}
            }

            final_state = self.graph.invoke(initial_state)

            researched_data = final_state["research_data"]

            return researched_data

        except Exception as e:
            
            raise CustomException(e,sys)