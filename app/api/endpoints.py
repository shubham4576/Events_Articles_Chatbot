from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.database import get_database, DatabaseOperations
from app.services import APIClient, VectorStoreService
from app.models.schemas import APIRequestSchema, APIResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/fetch-and-update", response_model=APIResponseSchema)
async def fetch_and_update_data(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    data_type: str = Query("all", description="Type of data to fetch: 'event', 'article', or 'all'"),
    db: Session = Depends(get_database)
):
    """
    Fetch data from external API, update SQLite database, and create embeddings in ChromaDB.
    
    This endpoint:
    1. Fetches data from the external API
    2. Updates/creates records in SQLite database (events and articles tables)
    3. Creates embeddings for articles in ChromaDB using Gemini
    
    Args:
        start_date: Start date for data fetching (YYYY-MM-DD)
        end_date: End date for data fetching (YYYY-MM-DD)
        data_type: Type of data to fetch ('event', 'article', or 'all')
        db: Database session dependency
    
    Returns:
        APIResponseSchema with processing results
    """
    try:
        logger.info(f"Starting data fetch and update process. Date range: {start_date} to {end_date}, Type: {data_type}")
        
        # Initialize services
        api_client = APIClient()
        vector_store = VectorStoreService()
        db_ops = DatabaseOperations(db)
        
        # Prepare API request
        api_request = APIRequestSchema(
            start_date=start_date,
            end_date=end_date,
            type=data_type
        )
        
        # Step 1: Fetch data from external API
        logger.info("Fetching data from external API...")
        api_data = await api_client.fetch_data(api_request)
        
        # Step 2: Parse API response
        logger.info("Parsing API response...")
        parsed_data = api_client.parse_api_response(api_data)
        
        events = parsed_data.get('events', [])
        articles = parsed_data.get('articles', [])
        
        logger.info(f"Found {len(events)} events and {len(articles)} articles in API response")
        
        # Step 3: Update SQLite database
        events_processed = 0
        articles_processed = 0
        
        # Process events
        if events and data_type in ['all', 'event']:
            logger.info("Processing events...")
            for event_data in events:
                try:
                    db_ops.create_or_update_event(event_data)
                    events_processed += 1
                except Exception as e:
                    logger.error(f"Failed to process event: {e}")
                    continue
        
        # Process articles
        if articles and data_type in ['all', 'article']:
            logger.info("Processing articles...")
            for article_data in articles:
                try:
                    db_ops.create_or_update_article(article_data)
                    articles_processed += 1
                except Exception as e:
                    logger.error(f"Failed to process article: {e}")
                    continue
        
        # Step 4: Create embeddings for articles in ChromaDB
        embeddings_created = 0
        if articles and data_type in ['all', 'article']:
            logger.info("Creating embeddings for articles...")
            try:
                embeddings_created = await vector_store.add_articles(articles)
            except Exception as e:
                logger.error(f"Failed to create embeddings: {e}")
                # Don't fail the entire operation if embeddings fail
        
        logger.info(f"Data processing completed. Events: {events_processed}, Articles: {articles_processed}, Embeddings: {embeddings_created}")
        
        return APIResponseSchema(
            success=True,
            message="Data fetched and updated successfully",
            events_processed=events_processed,
            articles_processed=articles_processed,
            embeddings_created=embeddings_created,
            data={
                "total_events_found": len(events),
                "total_articles_found": len(articles),
                "date_range": f"{start_date} to {end_date}",
                "data_type": data_type
            }
        )
        
    except Exception as e:
        logger.error(f"Error in fetch_and_update_data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch and update data: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Events Articles Chatbot API is running"}
