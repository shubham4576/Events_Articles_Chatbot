from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic event information (from API)
    post_title = Column(String(500), nullable=False, index=True)  # post_title from API
    post_content = Column(Text)  # post_content from API
    enabled = Column(String(10))  # enabled from API

    # Event specific details
    event_dates = Column(String(500))  # event_dates from API
    event_logo = Column(String(1000))  # event_logo from API
    location = Column(String(500))  # location from API
    venue = Column(String(500))  # venue from API
    url = Column(String(1000))  # url from API

    # Social media fields
    twitter_handle = Column(String(100))  # twitter_handle from API
    twitter_tag = Column(String(200))  # twitter_tag from API

    # User/Author information
    user_id = Column(String(50))  # user_id from API
    user_login = Column(String(200))  # user_login from API
    user_email = Column(String(200))  # user_email from API
    display_name = Column(String(200))  # display_name from API

    # Author details
    author_booth_numbers = Column(String(200))  # author_booth_numbers from API
    author_company_contact_name = Column(
        String(200)
    )  # author_company_contact_name from API
    author_company_name__title = Column(
        String(300)
    )  # author_company_name__title from API
    author_event = Column(String(50))  # author_event from API
    author_phone_number = Column(String(50))  # author_phone_number from API
    author_url = Column(String(1000))  # author_url from API

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Event(id={self.id}, post_title='{self.post_title}')>"


class Article(Base):
    __tablename__ = "articles"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Basic article information (from API)
    post_title = Column(String(500), index=True)  # post_title from API
    post_content = Column(Text)  # post_content from API

    # Content descriptions (for embeddings)
    keywords = Column(Text)  # keywords from API
    short_description = Column(Text)  # short_description from API
    social_media_description = Column(Text)  # social_media_description from API
    twitter_description = Column(Text)  # twitter_description from API

    # Social and external links
    social_name = Column(String(200))  # social_name from API
    url = Column(String(1000))  # url from API

    # User/Author information
    user_id = Column(String(50))  # user_id from API
    user_login = Column(String(200))  # user_login from API
    user_email = Column(String(200))  # user_email from API
    display_name = Column(String(200))  # display_name from API

    # Author details
    author_booth_numbers = Column(String(200))  # author_booth_numbers from API
    author_company_contact_name = Column(
        String(200)
    )  # author_company_contact_name from API
    author_company_name__title = Column(
        String(300)
    )  # author_company_name__title from API
    author_event = Column(String(50))  # author_event from API
    author_phone_number = Column(String(50))  # author_phone_number from API
    author_url = Column(String(1000))  # author_url from API

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Article(id={self.id}, post_title='{self.post_title}')>"
