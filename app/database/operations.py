import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.database_models import Article, Event

logger = logging.getLogger(__name__)


class DatabaseOperations:
    """Database operations for events and articles."""

    def __init__(self, db: Session):
        self.db = db

    def create_or_update_event(self, event_data: Dict[str, Any]) -> Event:
        """Create or update an event in the database."""
        try:
            # Fields to exclude from database storage for events
            excluded_fields = {"post_id", "type"}

            # Check if event exists (using post_title as unique identifier)
            post_title = event_data.get("post_title")

            existing_event = None
            if post_title:
                existing_event = (
                    self.db.query(Event).filter(Event.post_title == post_title).first()
                )

            # Filter out excluded fields and fields not in the model
            filtered_data = {}
            for key, value in event_data.items():
                if key not in excluded_fields and hasattr(Event, key) and key != "id":
                    filtered_data[key] = value

            if existing_event:
                # Update existing event
                for key, value in filtered_data.items():
                    setattr(existing_event, key, value)
                self.db.commit()
                self.db.refresh(existing_event)
                logger.info(f"Updated existing event: {existing_event.post_title}")
                return existing_event
            else:
                # Create new event
                event = Event(**filtered_data)
                self.db.add(event)
                self.db.commit()
                self.db.refresh(event)
                logger.info(f"Created new event: {event.post_title}")
                return event

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error creating/updating event: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in create_or_update_event: {e}")
            raise

    def create_or_update_article(self, article_data: Dict[str, Any]) -> Article:
        """Create or update an article in the database."""
        try:
            # Fields to exclude from database storage for articles
            excluded_fields = {"post_id", "category", "file", "type"}

            # Check if article exists (using post_title as unique identifier)
            post_title = article_data.get("post_title")

            existing_article = None
            if post_title:
                existing_article = (
                    self.db.query(Article)
                    .filter(Article.post_title == post_title)
                    .first()
                )

            # Filter out excluded fields and fields not in the model
            filtered_data = {}
            for key, value in article_data.items():
                if key not in excluded_fields and hasattr(Article, key) and key != "id":
                    filtered_data[key] = value

            if existing_article:
                # Update existing article
                for key, value in filtered_data.items():
                    setattr(existing_article, key, value)
                self.db.commit()
                self.db.refresh(existing_article)
                logger.info(f"Updated existing article: {existing_article.post_title}")
                return existing_article
            else:
                # Create new article
                article = Article(**filtered_data)
                self.db.add(article)
                self.db.commit()
                self.db.refresh(article)
                logger.info(f"Created new article: {article.post_title}")
                return article

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error creating/updating article: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error in create_or_update_article: {e}")
            raise

    def get_all_events(self) -> List[Event]:
        """Get all events from the database."""
        return self.db.query(Event).all()

    def get_all_articles(self) -> List[Article]:
        """Get all articles from the database."""
        return self.db.query(Article).all()

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get an event by ID."""
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Get an article by ID."""
        return self.db.query(Article).filter(Article.id == article_id).first()
