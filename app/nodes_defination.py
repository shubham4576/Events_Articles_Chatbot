import json
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import re
from html import unescape
from app.llm import AiService

# Initialize LLM
model = AiService().llm()

# Initialize database connection
json_file_path = Path(__file__).resolve().parent.parent / "data" / "data.json"


class STATE(BaseModel):
    user_query: str = ""
    keywords: list = []
    final_answer: str = ""
    list_of_json_object: str = ""

class Keywords(BaseModel):
    keywords: list[str] = Field(..., description="List of keywords extracted from the user query")

def clean_keywords(raw_keywords):
    """
    Cleans up messy keyword input like:
    ["[\"event\"", "legalweek", "west", "2017]"]
    and returns a list like: ["event", "legalweek", "west", "2017"]
    """
    # Join and try to parse as JSON if it's a stringified list
    joined = ' '.join(raw_keywords)
    try:
        # Find the embedded JSON array string
        match = re.search(r'\[(.*?)\]', joined)
        if match:
            content = '[' + match.group(1) + ']'
            # Replace single quotes with double in case needed
            content = content.replace("'", '"')
            return json.loads(content)
    except Exception:
        pass

    # Fallback: strip brackets and quotes manually
    cleaned = []
    for kw in raw_keywords:
        kw = kw.strip("[]\" ")
        if kw:
            cleaned.append(kw.lower())
    return cleaned

def get_keywords(state: STATE):
    user_query = state.user_query

    SYSTEM_PROMPT = """
    You are an AI assistant that extracts important keywords from user queries for full-text search over JSON data.

    Your task:
    - Output only a list of meaningful keywords from the user input.
    - Do NOT return explanations, sentences, or any extra formatting.
    - Remove stop words and unimportant connectors (e.g., 'the', 'and', 'of', etc.).
    - Keep relevant nouns, verbs, named entities, and domain-specific terms.
    - All keywords should be in lowercase.
    - Output format: ["keyword1", "keyword2", "keyword3"]
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "User Query: {user_query}"),
        ]
    )

    # parser = PydanticOutputParser(pydantic_object=Keywords)

    chain = prompt | model | CommaSeparatedListOutputParser()

    response = chain.invoke({"user_query": user_query})
    state.keywords = clean_keywords(response)
    return state


def full_text_search(state: STATE):
    keywords = state.keywords
    print(f"Searching for keywords: {keywords}")
    
    try:
        json_list = json.load(open(json_file_path, "r"))
        print(f"Loaded {len(json_list)} items from data file")
    except Exception as e:
        print(f"Error loading data file: {e}")
        state.list_of_json_object = "[]"
        return state

    def flatten(obj):
        """Recursively extract all text from JSON object (flatten nested dicts/lists)."""
        if isinstance(obj, dict):
            return ' '.join(flatten(v) for v in obj.values())
        elif isinstance(obj, list):
            return ' '.join(flatten(item) for item in obj)
        elif isinstance(obj, str):
            return clean_text(obj)
        else:
            return str(obj)

    def clean_text(text):
        """Remove HTML tags and normalize whitespace."""
        # Unescape HTML entities
        text = unescape(text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        return ' '.join(text.split()).lower()

    def calculate_relevance_score(text, keywords):
        """Calculate relevance score based on keyword frequency and position."""
        text_lower = text.lower()
        score = 0
        
        for keyword in keywords:
            # Count keyword occurrences
            count = text_lower.count(keyword.lower())
            score += count * 10  # Base score for each occurrence
            
            # Bonus for exact phrase matches
            if keyword.lower() in text_lower:
                score += 5
                
            # Bonus for keywords appearing in title or beginning
            if text_lower.startswith(keyword.lower()):
                score += 20
                
        return score

    # Normalize keywords for case-insensitive matching
    keywords = [kw.lower() for kw in keywords]
    print(f"Normalized keywords: {keywords}")

    # Score and collect matching items
    scored_results = []
    for i, item in enumerate(json_list):
        combined_text = flatten(item)
        
        # Check if any keyword matches
        if any(kw in combined_text for kw in keywords):
            score = calculate_relevance_score(combined_text, keywords)
            scored_results.append((score, item, i))
    
    # Sort by relevance score (highest first) and take top 50
    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_results[:50]
    
    # Extract just the items from the top results
    results = [item for score, item, index in top_results]
    
    print(f"Found {len(scored_results)} total matches, returning top 50")
    print(f"Top 5 scores: {[score for score, _, _ in top_results[:5]]}")
    
    state.list_of_json_object = str(results)
    return state


def get_answer(state: STATE):
    list_of_json_object = state.list_of_json_object
    user_query = state.user_query

    SYSTEM_PROMPT = """
    You are an authoritative AI assistant that provides direct, confident answers based on the provided JSON data.

    Instructions:
    - Give direct, clear, and confident answers without unnecessary hedging or uncertainty.
    - Use the JSON data to provide authoritative responses that users can trust.
    - Be concise and to the point - avoid lengthy explanations unless specifically requested.
    - Present information as factual and approved, not as tentative suggestions.
    - If the data contains relevant information, present it confidently as the answer.
    - Only say "No relevant information found" if the data truly contains nothing related to the query.
    - Use professional, authoritative language that conveys expertise and reliability.
    - Structure responses logically with clear points when multiple pieces of information are relevant.

    Input: <user query>
    Data: <JSON>
    Answer: <direct, authoritative response based on JSON data>
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "User Query: {user_query}\nJSON Data: {list_of_json_object}"),
        ]
    )

    chain = prompt | model | StrOutputParser()
    response = chain.invoke({"user_query": user_query, "list_of_json_object": list_of_json_object})
    state.final_answer = response
    return state



