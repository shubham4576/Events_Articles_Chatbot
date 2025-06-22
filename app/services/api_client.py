import logging
from typing import Any, Dict, List

import httpx

from app.config import settings
from app.models.schemas import APIRequestSchema

logger = logging.getLogger(__name__)


class APIClient:
    """Client for fetching data from the external API."""

    def __init__(self):
        self.base_url = settings.api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": settings.api_auth_header,
            "Cookie": "PHPSESSID=1158a7ca22393d489c8828eb2f9a580f; __cf_bm=P_5fUwzg8oS.ApSniDHDDd74soIp1yA1Z0irVZ6MkaI-1748187878-1.0.1.1-kqbe8ty54ZZlm8igFyZB3XXDZDoZmg3PAW4Orqf1NAB6hxeN4pWYh6MEcYxtxPxg1g_zFvtofbuvZsgEbb5dkmZup8nXZce5x_8rGtphg8Y; __cf_bm=aAPOi2xPypaWZRRADxaZSzr4BkfFJD1IiB5Ic1Jg6X4-1750589197-1.0.1.1-aUndY7nbktzZgjc.RmIa61xY86or6ncXd4NrNHf0X7Uta.rq5tHsW0Fg2qjbpT9dmR0UlBkpBQHa.iuKChVG07Suz7Di0g2TEEt3RX6iVFQ; __cf_bm=ezwyP29WUwBin8Y.PHtuEtKQr.Se1vQIw_tPSx0eToM-1750612897-1.0.1.1-6GzWT1bZElFn0w60kK3ZW_i00oo5bjsVH5DzqG9UkBZJpOLQnZR7lHcq4jaqJpjAhIANCfxzOizUV90vKlVH5xfcb2uImIiIACOG6itclRQ",
        }

    async def fetch_data(self, request_data: APIRequestSchema) -> Dict[str, Any]:
        """
        Fetch data from the external API.

        Args:
            request_data: API request parameters

        Returns:
            Dictionary containing the API response

        Raises:
            httpx.HTTPError: If the API request fails
        """
        payload = {
            "start_date": request_data.start_date,
            "end_date": request_data.end_date,
            "type": request_data.type,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching data from API with payload: {payload}")

                response = await client.post(
                    self.base_url, json=payload, headers=self.headers
                )

                response.raise_for_status()
                data = response.json()

                logger.info(
                    f"Successfully fetched data from API. Response status: {response.status_code}"
                )
                return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching data: {e}")
            raise

    def parse_api_response(
        self, api_data: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse the API response and separate events and articles.

        Args:
            api_data: Raw API response data (list of items)

        Returns:
            Dictionary with 'events' and 'articles' lists
        """
        events = []
        articles = []

        # The API returns a direct list of items with a 'type' field
        items = api_data if isinstance(api_data, list) else []

        for item in items:
            if not item:
                continue

            item_type = item.get("type", "").lower()

            if item_type == "event":
                # Keep all fields except excluded ones (post_id, type)
                event_data = {
                    k: v for k, v in item.items() if k not in ["post_id", "type"]
                }
                events.append(event_data)
            elif item_type == "article":
                # Keep all fields except excluded ones (post_id, category, file, type)
                article_data = {
                    k: v
                    for k, v in item.items()
                    if k not in ["post_id", "category", "file", "type"]
                }
                articles.append(article_data)

        logger.info(
            f"Parsed {len(events)} events and {len(articles)} articles from API response"
        )

        return {"events": events, "articles": articles}
