from langchain.chat_models import init_chat_model


def setup_llm():
    return init_chat_model(
        model='google_genai:gemini-3.5-flash-lite',
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )