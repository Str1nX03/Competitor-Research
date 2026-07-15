from typing import TypedDict, List, Dict
from src.utils import get_llm
from langchain_core.prompts import ChatPromptTemplate
from src.exception import CustomException
from langgraph.graph import StateGraph, START, END
from src.prompts.reporter_prompt import REPORT_GENERATOR_PROMPT
import sys

class AgentState(TypedDict):
    
    research_data: Dict[str, List[str]]
    reports: List[str]

class ReporterAgent:
    
    def __init__(self):
        
        self.llm = get_llm(max_token = 2000)
        self.graph = self._build_graph()

    def _generate_report(self, state: AgentState):

        try:

            research_data = state["research_data"]
            reports = []
            prompt = ChatPromptTemplate.from_template(REPORT_GENERATOR_PROMPT)

            for name, research_data in research_data.items():

                response = self.llm.invoke(prompt.format(
                    research_data = research_data
                ))

                reports.append(response.content)

            return {"reports": reports}

        except Exception as e:

            raise CustomException(e,sys)

    def _build_graph(self):

        try:

            graph = StateGraph(AgentState)

            graph.add_node("generate_report", self._generate_report)

            graph.add_edge(START, "generate_report")
            graph.add_edge("generate_report", END)

            return graph.compile()

        except Exception as e:

            raise CustomException(e,sys)

    def run(self, research_data: Dict[str, List[str]]):

        try:

            initial_state = {
                "research_data": research_data,
                "reports": []
            }

            final_state = self.graph.invoke(initial_state)

            report = final_state["reports"]

            return report
        
        except Exception as e:

            raise CustomException(e,sys)