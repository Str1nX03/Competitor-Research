from typing import TypedDict, List, Dict
from src.utils import get_llm, web_search
from langchain_core.prompts import ChatPromptTemplate
from src.exception import CustomException
import sys
import json
import re
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

            query = f"Top competitors and products in the space of {user_input}"

            competitor_data = web_search(query)

            # Join list into clean readable text for the LLM
            context_text = "\n\n".join(competitor_data) if competitor_data else "No data found."

            prompt = ChatPromptTemplate.from_template(COMPETITOR_EXTRACT_PROMPT)

            response = self.llm.invoke(prompt.format(
                competitor_data = context_text
            ))
            content = response.content.strip()

            # DEBUG: Log what the LLM actually returns
            print(f"[DEBUG] Raw LLM response for competitor extraction:\n{content}\n{'='*50}")

            # Layer 1: Strip markdown code block wrappers if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            competitors = []

            # Layer 2: Try parsing as JSON object with "competitors" key
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "competitors" in parsed:
                    competitors = parsed["competitors"]
                elif isinstance(parsed, list):
                    competitors = parsed
            except json.JSONDecodeError:
                pass

            # Layer 3: Regex fallback — extract any JSON array from the full response
            if not competitors:
                match = re.search(r'\[.*?\]', content, re.DOTALL)
                if match:
                    try:
                        competitors = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        pass

            # Layer 4: Last resort — extract all double-quoted strings from the response
            if not competitors:
                quoted = re.findall(r'"([^"]{2,50})"', content)
                # Filter out common non-competitor strings
                ignore = {"competitors", "competitor 1", "competitor 2", "type", "object", "array", "string"}
                competitors = [q for q in quoted if q.lower() not in ignore]

            # Ensure we have a clean list of strings
            competitors = [str(c).strip() for c in competitors if isinstance(c, str) and len(str(c).strip()) > 1]

            print(f"[DEBUG] Extracted competitors: {competitors}")

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