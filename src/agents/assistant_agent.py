from typing import TypedDict, List
from src.utils import get_llm, web_search
from langchain_core.prompts import ChatPromptTemplate
from src.exception import CustomException
import sys
import json
from langgraph.graph import StateGraph, START, END
from src.prompts.assistant_prompt import INTENT_DETECTION_PROMPT, CONTEXT_RETRIEVAL_PROMPT

class AgentState(TypedDict):

    user_input: str
    user_intent: str
    context: List[str]

class AssistantAgent:

    def __init__(self):
        
        self.llm = get_llm()
        self.graph = self._build_graph()

    def _intent_detector(self, state: AgentState) -> dict:
        """
        This method is used to detect the intent of the user.
        """
        try:

            user_input = state["user_input"]

            prompt = ChatPromptTemplate.from_template(INTENT_DETECTION_PROMPT)

            response = self.llm.invoke(prompt.format(
                user_input = user_input
                ))
            
            return {"user_intent": response.content}

        except Exception as e:
            raise CustomException(e,sys)

    def _get_context(self, state: AgentState) -> dict:
        """
        This method is used to get the context of the user query.
        """
        try:

            user_input = state["user_input"]
            user_intent = state["user_intent"]

            prompt = ChatPromptTemplate.from_template(CONTEXT_RETRIEVAL_PROMPT)

            response = self.llm.invoke(prompt.format(
                user_input = user_input,
                user_intent = user_intent
            ))

            questions = json.loads(response.content)
            context = []

            for question in questions:

                results = web_search(question)

                for ans in results:

                    context.append(ans)

            return {"context": context}

        except Exception as e:
            raise CustomException(e,sys)

    def _build_graph(self):

        try:

            graph = StateGraph(AgentState)

            graph.add_node("intent_detector", self._intent_detector)
            graph.add_node("get_context", self._get_context)

            graph.add_edge(START, "intent_detector")
            graph.add_edge("intent_detector", "get_context")
            graph.add_edge("get_context", END)

            return graph.compile()

        except Exception as e:

            raise CustomException(e,sys)

    def run(self, user_input: str) -> list[str]:
        """
        This method is used to run the agent.
        Args:
            user_query (str): The user query.
        Returns:
            list: The context of the user query using real world information.
        """
        initial_state = {
            "user_input": user_input,
            "context": []
        }
        final_state = self.graph.invoke(initial_state)

        return final_state["context"]