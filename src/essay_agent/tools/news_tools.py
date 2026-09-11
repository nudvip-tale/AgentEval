import requests
from GoogleNews import GoogleNews

def get_related_news(
    topic,
    start="06/01/2025",
    end="06/10/2025",
    full_content=False,
    auto_extract_keywords="llm",
    calculate_news_relevancy=True,
    disable_internal_timeouts=False,
    session_id="null",
    user_id="null",
):
    google_news = GoogleNews(lang = 'en', region = 'india', start = start, end = end)
    google_news.search(topic)
    results = google_news.result()
    print("\nNews tool called \n")
    if len(results) == 0:
        print("No news articles found for the given topic.")
        return []
    else:
        return [res['title'] for res in results[ : 5]]