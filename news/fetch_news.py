import os
from typing import Any, Dict

from api.news_api_utils import get_url, parse_using_trafilatura

BASE_URL = "https://gnews.io/api/v4"
DEFAULT_QUERY_PARAMS = {
    "lang": "en",
    "country": "in",
    "max": 10,
}


def get_news_on_query(query: Dict):
    api_key = os.getenv("GNEWS_API_KEY")
    final_query = {
        **DEFAULT_QUERY_PARAMS,
        "apikey": api_key,
        **query,
    }

    news_response = get_url(f"{BASE_URL}/search", final_query)
    first_article = None

    if news_response and news_response.get("articles"):
        first_article = news_response["articles"][0]

    if first_article and first_article.get("url"):
        return parse_using_trafilatura(first_article["url"])

    return None
