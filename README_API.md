# Events Articles Chatbot API

This FastAPI application fetches data from an external API, stores it in SQLite database, and creates embeddings in ChromaDB for a chatbot system.

## Features

- **Data Fetching**: Retrieves events and articles from external API
- **SQLite Storage**: Stores events and articles in separate tables
- **Vector Embeddings**: Creates embeddings for articles using Google Gemini
- **ChromaDB Integration**: Stores article embeddings for similarity search
- **RESTful API**: FastAPI endpoints for data management

## Project Structure

```
app/
├── api/
│   ├── __init__.py
│   └── endpoints.py          # FastAPI endpoints
├── config/
│   ├── __init__.py
│   └── settings.py           # Application settings
├── database/
│   ├── __init__.py
│   ├── connection.py         # Database connection
│   └── operations.py         # Database CRUD operations
├── models/
│   ├── __init__.py
│   ├── database_models.py    # SQLAlchemy models
│   └── schemas.py            # Pydantic schemas
├── services/
│   ├── __init__.py
│   ├── api_client.py         # External API client
│   └── vector_store.py       # ChromaDB service
└── __init__.py
main.py                       # FastAPI application entry point
requirements.txt              # Python dependencies
.env.example                  # Environment variables template
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` file:
```
GOOGLE_API_KEY=your_google_api_key_here
SQLITE_DB_PATH=data/events_articles.db
CHROMADB_PATH=data/chromadb
DEBUG=false
```

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### GET /api/v1/fetch-and-update

Fetches data from external API and updates local storage.

**Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format  
- `data_type` (optional): Type of data to fetch ('event', 'article', or 'all')

**Example:**
```bash
curl "http://localhost:8000/api/v1/fetch-and-update?start_date=2024-01-01&end_date=2025-12-31&data_type=all"
```

**Response:**
```json
{
  "success": true,
  "message": "Data fetched and updated successfully",
  "events_processed": 10,
  "articles_processed": 25,
  "embeddings_created": 25,
  "data": {
    "total_events_found": 10,
    "total_articles_found": 25,
    "date_range": "2024-01-01 to 2025-12-31",
    "data_type": "all"
  }
}
```

### GET /api/v1/health

Health check endpoint.

### GET /

Root endpoint with API information.

## Database Schema

### Events Table (Comprehensive)
- **Primary Key**: id
- **Basic Info**: title, slug, content, excerpt
- **SEO/Social**: short_description, social_media_description, twitter_description, meta_description, keywords
- **Event Details**: event_date, event_end_date, event_time, location, venue, address, city, state, country, postal_code
- **Organizer**: organizer, organizer_email, organizer_phone, organizer_website
- **Pricing**: ticket_price, currency, registration_link, registration_required, max_attendees
- **Media**: image_url, featured_image, gallery_images, video_url, website_url
- **Classification**: category, tags, event_type
- **Status**: status, published_date, featured
- **Timestamps**: created_at, updated_at

### Articles Table (Comprehensive)
- **Primary Key**: id
- **Basic Info**: title, slug, content, excerpt
- **SEO/Social**: short_description, social_media_description, twitter_description, meta_description, keywords
- **Author**: author, author_email, author_bio, published_date, modified_date
- **Classification**: category, subcategory, tags, article_type
- **Media**: image_url, featured_image, gallery_images, video_url, audio_url
- **SEO Metadata**: meta_title, canonical_url, reading_time, word_count
- **Social Sharing**: social_image, twitter_card_type, og_type
- **Status**: status, featured, sticky, allow_comments
- **Analytics**: view_count, like_count, share_count
- **External**: source_url, external_link, related_articles
- **Timestamps**: created_at, updated_at

### Excluded Fields
- **Events**: post_id, type
- **Articles**: post_id, category (WordPress), file, type

## Vector Store

Articles are stored in ChromaDB with:
- **Embedding Fields**: short_description, social_media_description, twitter_description, keywords
- **Metadata Fields**: All other article fields (except post_id, category, file)
- **Embedding Model**: Google Gemini text-embedding-004

## Data Processing

1. **API Fetch**: Retrieves data from external API with authentication
2. **Data Parsing**: Separates events and articles, filters excluded fields
3. **Database Update**: Creates or updates records in SQLite
4. **Embedding Creation**: Generates embeddings for articles using Gemini
5. **Vector Storage**: Stores embeddings in ChromaDB for similarity search

## Error Handling

- Comprehensive logging throughout the application
- Graceful error handling for API failures
- Database transaction rollback on errors
- Partial success handling (continues processing if some items fail)

## Next Steps

This API serves as the foundation for:
- SQL Agent for database queries
- Agentic RAG for article retrieval
- LangGraph-based chatbot implementation
