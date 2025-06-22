import os
import chromadb
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing ChromaDB vector store with Gemini embeddings."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize_chromadb()
        self._initialize_gemini()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Ensure the ChromaDB directory exists
            if not os.path.exists(settings.chromadb_path):
                os.makedirs(settings.chromadb_path, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=settings.chromadb_path)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chromadb_collection_name,
                metadata={"description": "Articles collection for chatbot"}
            )
            
            logger.info(f"ChromaDB initialized successfully. Collection: {settings.chromadb_collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _initialize_gemini(self):
        """Initialize Google Gemini API."""
        try:
            if not settings.google_api_key:
                raise ValueError("Google API key not provided in settings")
            
            genai.configure(api_key=settings.google_api_key)
            logger.info("Gemini API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            raise
    
    def _create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text using Gemini.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            result = genai.embed_content(
                model=f"models/{settings.gemini_model}",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise
    
    def _prepare_article_text(self, article: Dict[str, Any]) -> str:
        """
        Prepare article text for embedding by combining relevant fields.
        
        Args:
            article: Article data dictionary
            
        Returns:
            Combined text string for embedding
        """
        text_parts = []
        
        # Fields to include in embedding
        embedding_fields = [
            'short_description',
            'social_media_description', 
            'twitter_description',
            'keywords'
        ]
        
        for field in embedding_fields:
            value = article.get(field)
            if value and isinstance(value, str) and value.strip():
                text_parts.append(value.strip())
        
        # Combine all text parts
        combined_text = " ".join(text_parts)
        
        # If no text found, use title as fallback
        if not combined_text.strip():
            combined_text = article.get('title', '')
        
        return combined_text
    
    def _prepare_article_metadata(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare article metadata (fields not used for embedding).
        
        Args:
            article: Article data dictionary
            
        Returns:
            Metadata dictionary
        """
        # Fields to exclude from metadata (used in embedding or not needed)
        exclude_fields = {
            'short_description',
            'social_media_description',
            'twitter_description', 
            'keywords',
            'post_id',
            'category',
            'file'
        }
        
        metadata = {}
        for key, value in article.items():
            if key not in exclude_fields and value is not None:
                # Convert non-string values to strings for metadata
                if isinstance(value, (dict, list)):
                    metadata[key] = str(value)
                else:
                    metadata[key] = value
        
        return metadata
    
    async def add_articles(self, articles: List[Dict[str, Any]]) -> int:
        """
        Add articles to the vector store.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Number of articles successfully added
        """
        if not articles:
            return 0
        
        added_count = 0
        
        for i, article in enumerate(articles):
            try:
                # Prepare text for embedding
                text_for_embedding = self._prepare_article_text(article)
                
                if not text_for_embedding.strip():
                    logger.warning(f"No text found for embedding in article {i}")
                    continue
                
                # Create embedding
                embedding = self._create_embedding(text_for_embedding)
                
                # Prepare metadata
                metadata = self._prepare_article_metadata(article)
                
                # Generate unique ID for the article
                article_id = f"article_{article.get('id', i)}_{hash(article.get('title', ''))}"
                
                # Add to ChromaDB
                self.collection.add(
                    embeddings=[embedding],
                    documents=[text_for_embedding],
                    metadatas=[metadata],
                    ids=[article_id]
                )
                
                added_count += 1
                logger.debug(f"Added article {article_id} to vector store")
                
            except Exception as e:
                logger.error(f"Failed to add article {i} to vector store: {e}")
                continue
        
        logger.info(f"Successfully added {added_count} articles to vector store")
        return added_count
    
    def search_articles(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Search for similar articles in the vector store.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            Search results from ChromaDB
        """
        try:
            # Create embedding for the query
            query_embedding = self._create_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search articles: {e}")
            raise
