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
    # Join and try to parse as JSON if it’s a stringified list
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
    json_list = json.load(open(json_file_path, "r"))



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

    # Normalize keywords for case-insensitive matching
    keywords = [kw.lower() for kw in keywords]

    results = []
    for item in json_list:
        combined_text = flatten(item)
        if all(kw in combined_text for kw in keywords):
            results.append(item)

    print(f"List ::: {results}")
    state.list_of_json_object = str(results)
    return state


def get_answer(state: STATE):
    list_of_json_object = state.list_of_json_object
    user_query = state.user_query

    SYSTEM_PROMPT = """
    You are an AI assistant designed to answer user queries using the provided JSON data.

    Instructions:
    - Use only the given JSON data to answer the query truthfully.
    - Do not fabricate or assume any information not present in the data.
    - Keep your response clear, concise, and to the point.
    - Maintain a respectful and neutral tone at all times.
    - Avoid hateful speech, personal opinions, or unnecessary commentary.
    - If the answer cannot be found in the data, reply with: "No relevant information found in the provided data."

    Input: <user query>
    Data: <JSON>
    Answer: <accurate and respectful response based solely on JSON>
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



