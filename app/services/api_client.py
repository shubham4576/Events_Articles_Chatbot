import base64
import logging
from typing import Any, Dict, List

import requests

from app.config import settings
from app.models.schemas import APIRequestSchema

logger = logging.getLogger(__name__)


class APIClient:
    """Client for fetching data from the external API."""

    def __init__(self):
        self.base_url = settings.api_url

    def _get_headers(self) -> Dict[str, str]:
        """Dynamically generate headers including Basic Auth each time."""
        if settings.api_username and settings.api_password:
            credentials = f"{settings.api_username}:{settings.api_password}"
            print(credentials)
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
                "utf-8"
            )
            auth_header = f"Basic {encoded_credentials}"
            print("AUTH HEADER: ", auth_header)
        else:
            auth_header = settings.api_auth_header

        return {
            "Content-Type": "application/json",
            "Authorization": auth_header,
        }

    def fetch_data(self, request_data: APIRequestSchema) -> Dict[str, Any]:
        """
        Fetch data from the external API using synchronous `requests` library.

        Args:
            request_data: API request parameters

        Returns:
            Dictionary containing the API response

        Raises:
            requests.HTTPError: If the API request fails
        """
        url = self.base_url
        headers = self._get_headers()

        payload = request_data.model_dump()

        try:
            logger.info(f"Sending POST to {url} with payload: {payload}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            logger.info(f"API returned status {response.status_code}")
            return response.json()

        except requests.HTTPError as e:
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
