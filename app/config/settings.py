import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # API Configuration
    api_url: str = "https://theedgeroom.com/wp-json/custom/v1/search-data"
    api_auth_header: str = "Basic YWRtaW46bUdWcSBFeG9UIGZJdWsgRGF3ayB0VW5hIG9YaDg="
    # API Configuration - Option 2: Separate credentials
    api_username: Optional[str] = "admin"
    api_password: Optional[str] = "mGVq ExoT fIuk Dawk tUna oXh8"

    # Database Configuration
    sqlite_db_path: str = "data/events_articles.db"

    # ChromaDB Configuration
    chromadb_path: str = "data/chromadb"
    chromadb_collection_name: str = "articles"

    # Google Gemini Configuration
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = "text-embedding-004"

    # Application Configuration
    app_title: str = "Events Articles Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
