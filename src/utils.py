from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from src.exception import CustomException
from src.config import get_settings
import sys

settings = get_settings()

def get_llm(
    model: str | None = settings.GROQ_MODEL, 
    temperature: float | None = settings.GROQ_MODEL_TEMPERATURE, 
    max_token: int | None = settings.GROQ_MODEL_MAX_TOKEN
) -> ChatGroq:
    """
    Initializes and returns the main Large Language Model (LLM) instance.
    Uses the `openai/gpt-oss-20b` model by default via the Groq API.
    This model is best suited for complex reasoning and structured data extraction tasks.
    """
    try:
        llm = ChatGroq(
            model = model,
            temperature = temperature,
            max_tokens = max_token,
            api_key = settings.GROQ_API_KEY
        )
        return llm

    except Exception as e:
        raise CustomException(e,sys)

def web_search(
    query: str | None,
    max_results: int | None = 2,
    topic: str | None = "general"
) -> list[str]:
    """
    Performs a web search using the Tavily Search API.
    Returns a list of search results.
    """
    try:
        search = TavilySearch(
            max_results = max_results,
            topic = topic,
            api_key = settings.TAVILY_API_KEY
        )
        response = search.invoke(query)
        results = []

        for res in response["results"]:

            results.append(res["content"])
            
        return results
    
    except Exception as e:
        raise CustomException(e,sys)