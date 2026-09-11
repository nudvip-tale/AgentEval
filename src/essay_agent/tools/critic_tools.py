from src.essay_agent.llm.llm_proxy import setup_llm

critic_llm = setup_llm()

def critic_review(content: str) -> str:
    print("\n Review tool called\n\n")
    """
    Critic reviews the content and provides feedback if improvements are needed.
    If the content is good, reply 'Looks good.'
    content could be of keywords from a document or news articles 
    """
    prompt = (
        "You are a critic. Review the following content. "
        "If it can be improved, provide constructive feedback. "
        "If it is good, reply 'Looks good.'\n\ncontent:\n" + content
    )
    response = critic_llm.invoke([{"role": "user", "content": prompt}])
    return response.content