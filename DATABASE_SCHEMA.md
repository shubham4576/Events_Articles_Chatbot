# Database Schema Documentation

## Overview

This document describes the database schema for the Events Articles Chatbot system, designed to match the exact structure of the external API response. The schema includes two main tables: `events` and `articles`.

## API Data Structure

The API returns a direct array of objects, each with a `type` field indicating whether it's an "event" or "article".

## Excluded Fields

Based on your requirements, the following fields are excluded from database storage:

### Events
- `post_id` - WordPress post ID (excluded)
- `type` - Data type indicator (excluded)

### Articles
- `post_id` - WordPress post ID (excluded)
- `category` - WordPress category (excluded)
- `file` - File attachments (excluded)
- `type` - Data type indicator (excluded)

## Events Table Schema (Actual API Structure)

```sql
CREATE TABLE events (
    -- Primary Key
    id INTEGER PRIMARY KEY,

    -- Basic Event Information (from API)
    post_title VARCHAR(500) NOT NULL,  -- post_title from API
    post_content TEXT,                 -- post_content from API
    enabled VARCHAR(10),               -- enabled from API

    -- Event Specific Details
    event_dates VARCHAR(500),          -- event_dates from API
    event_logo VARCHAR(1000),          -- event_logo from API
    location VARCHAR(500),             -- location from API
    venue VARCHAR(500),                -- venue from API
    url VARCHAR(1000),                 -- url from API

    -- Social Media Fields
    twitter_handle VARCHAR(100),       -- twitter_handle from API
    twitter_tag VARCHAR(200),          -- twitter_tag from API

    -- User/Author Information
    user_id VARCHAR(50),               -- user_id from API
    user_login VARCHAR(200),           -- user_login from API
    user_email VARCHAR(200),           -- user_email from API
    display_name VARCHAR(200),         -- display_name from API

    -- Author Details
    author_booth_numbers VARCHAR(200),           -- author_booth_numbers from API
    author_company_contact_name VARCHAR(200),    -- author_company_contact_name from API
    author_company_name__title VARCHAR(300),     -- author_company_name__title from API
    author_event VARCHAR(50),                    -- author_event from API
    author_phone_number VARCHAR(50),             -- author_phone_number from API
    author_url VARCHAR(1000),                    -- author_url from API

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Articles Table Schema (Actual API Structure)

```sql
CREATE TABLE articles (
    -- Primary Key
    id INTEGER PRIMARY KEY,

    -- Basic Article Information (from API)
    post_title VARCHAR(500),           -- post_title from API
    post_content TEXT,                 -- post_content from API

    -- Content Descriptions (for embeddings)
    keywords TEXT,                     -- keywords from API
    short_description TEXT,            -- short_description from API
    social_media_description TEXT,     -- social_media_description from API
    twitter_description TEXT,          -- twitter_description from API

    -- Social and External Links
    social_name VARCHAR(200),          -- social_name from API
    url VARCHAR(1000),                 -- url from API

    -- User/Author Information
    user_id VARCHAR(50),               -- user_id from API
    user_login VARCHAR(200),           -- user_login from API
    user_email VARCHAR(200),           -- user_email from API
    display_name VARCHAR(200),         -- display_name from API

    -- Author Details
    author_booth_numbers VARCHAR(200),           -- author_booth_numbers from API
    author_company_contact_name VARCHAR(200),    -- author_company_contact_name from API
    author_company_name__title VARCHAR(300),     -- author_company_name__title from API
    author_event VARCHAR(50),                    -- author_event from API
    author_phone_number VARCHAR(50),             -- author_phone_number from API
    author_url VARCHAR(1000),                    -- author_url from API

    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## ChromaDB Vector Store

For articles, the following fields are used for embedding creation:
- `keywords`
- `short_description`
- `social_media_description`
- `twitter_description`

All other article fields (except excluded ones: post_id, category, file, type) are stored as metadata in ChromaDB.

## Indexes

The following indexes are automatically created:
- `events.id` (Primary Key)
- `events.post_title` (Index)
- `articles.id` (Primary Key)
- `articles.post_title` (Index)

## Data Processing Notes

1. **Duplicate Handling**: Records are identified by `post_title` for both events and articles
2. **Field Filtering**: Only fields that exist in the model are stored
3. **Excluded Fields**: Specified fields (post_id, category, file, type) are automatically filtered out during processing
4. **Embedding Creation**: Only articles are processed for vector embeddings using Gemini text-embedding-004
5. **API Structure**: The API returns a direct array of objects with type indicators

## Usage in Chatbot System

This schema supports:
- **SQL Agent**: Can query structured data from events and articles tables
- **Agentic RAG**: Can retrieve similar articles using vector embeddings
- **LangGraph Integration**: Provides structured data for conversation context
