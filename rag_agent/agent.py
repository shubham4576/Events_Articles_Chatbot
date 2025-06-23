"""
RAG Agent for semantic search and article retrieval.
"""

import logging
from typing import Dict, Any, List, Optional

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage

from app.services.vector_store import VectorStoreService
from app.config import settings

logger = logging.getLogger(__name__)


class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent for semantic search.
    
    This agent can:
    - Perform semantic search on articles using embeddings
    - Generate contextual responses based on retrieved documents
    - Handle follow-up questions with context
    - Provide source attribution
    """
    
    def __init__(self):
        """Initialize the RAG Agent."""
        self.model = None
        self.vector_store = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the RAG agent with vector store and language model."""
        try:
            # Initialize the language model
            self.model = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
            
            # Initialize vector store service
            self.vector_store = VectorStoreService()
            
            logger.info("RAG Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Agent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the RAG agent."""
        return """
You are a specialized RAG agent for retrieving and discussing articles from an events and articles database.

Your capabilities:
1. Semantic search through article content using embeddings
2. Contextual understanding of user queries
3. Providing detailed responses based on retrieved articles
4. Source attribution and transparency

Instructions:
- Use the retrieved articles to provide comprehensive, accurate answers
- Always cite your sources when referencing specific articles
- If retrieved content doesn't fully answer the question, acknowledge limitations
- Provide relevant context and background information
- Be conversational but informative
- If no relevant articles are found, suggest alternative search terms

Response format:
- Start with a direct answer to the user's question
- Provide supporting details from the retrieved articles
- Include source attribution (article titles, authors when available)
- End with suggestions for related topics if appropriate

Remember: You're helping users discover and understand content from articles. Be helpful, accurate, and transparent about your sources.
        """.strip()
    
    def query(self, user_query: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Process a user query using RAG approach.
        
        Args:
            user_query: The user's natural language query
            n_results: Number of similar articles to retrieve
            
        Returns:
            Dictionary containing RAG results and generated response
        """
        try:
            logger.info(f"Processing RAG query: {user_query}")
            
            # Retrieve similar articles
            search_results = self.vector_store.search_articles(user_query, n_results)
            
            if not search_results or not search_results.get('documents'):
                return {
                    "success": True,
                    "response": "I couldn't find any relevant articles for your query. Try rephrasing your question or using different keywords.",
                    "agent_type": "rag",
                    "query": user_query,
                    "retrieved_docs": [],
                    "search_results": search_results
                }
            
            # Prepare context from retrieved documents
            context = self._prepare_context(search_results)
            
            # Generate response using LLM with context
            response = self._generate_response(user_query, context)
            
            return {
                "success": True,
                "response": response,
                "agent_type": "rag",
                "query": user_query,
                "retrieved_docs": self._format_retrieved_docs(search_results),
                "search_results": search_results
            }
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": "rag",
                "query": user_query,
                "response": f"I encountered an error while searching for articles: {str(e)}"
            }
    
    def _prepare_context(self, search_results: Dict[str, Any]) -> str:
        """
        Prepare context string from search results.
        
        Args:
            search_results: Results from vector store search
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        documents = search_results.get('documents', [[]])[0]
        metadatas = search_results.get('metadatas', [[]])[0]
        distances = search_results.get('distances', [[]])[0]
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            title = metadata.get('title', f'Article {i+1}')
            author = metadata.get('author', 'Unknown')
            
            context_parts.append(f"""
Article {i+1}: {title}
Author: {author}
Relevance Score: {1 - distance:.3f}
Content: {doc[:500]}...
---
            """.strip())
        
        return "\n\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str) -> str:
        """
        Generate response using LLM with retrieved context.
        
        Args:
            query: User's original query
            context: Context from retrieved documents
            
        Returns:
            Generated response
        """
        try:
            system_prompt = self._get_system_prompt()
            
            user_prompt = f"""
Based on the following retrieved articles, please answer this question: {query}

Retrieved Articles:
{context}

Please provide a comprehensive answer based on the retrieved content, citing specific articles when relevant.
            """.strip()
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.model.invoke(messages)
            
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, dict) and 'content' in response:
                return response['content']
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return f"I found relevant articles but encountered an error generating the response: {str(e)}"
    
    def _format_retrieved_docs(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format retrieved documents for response.
        
        Args:
            search_results: Raw search results from vector store
            
        Returns:
            List of formatted document information
        """
        formatted_docs = []
        
        documents = search_results.get('documents', [[]])[0]
        metadatas = search_results.get('metadatas', [[]])[0]
        distances = search_results.get('distances', [[]])[0]
        
        for doc, metadata, distance in zip(documents, metadatas, distances):
            formatted_docs.append({
                'title': metadata.get('title', 'Untitled'),
                'author': metadata.get('author', 'Unknown'),
                'relevance_score': round(1 - distance, 3),
                'content_preview': doc[:200] + "..." if len(doc) > 200 else doc,
                'metadata': metadata
            })
        
        return formatted_docs
    
    def is_rag_query(self, query: str) -> bool:
        """
        Determine if a query is likely to need RAG/semantic search.
        
        Args:
            query: User query to analyze
            
        Returns:
            True if query likely needs RAG approach
        """
        rag_keywords = [
            "about", "explain", "tell me", "what is", "how does", "why",
            "content", "article", "information", "details", "description",
            "similar", "related", "like", "compare", "difference",
            "topic", "subject", "theme", "concept", "idea"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in rag_keywords)
