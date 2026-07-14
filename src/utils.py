from langchain_groq import ChatGroq
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