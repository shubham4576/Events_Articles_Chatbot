import re
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.fetcher import fetch_and_save_data
from pathlib import Path
from app.router_workflow import workflow

BASE_PATH = Path(__file__).resolve().parent
print(BASE_PATH)

app = FastAPI()

STATIC_RESPONSES = {
    r"(?i)\b(hi|hello|hey)\b": "Hello! How can I assist you today?",
    r"(?i)\b(how are you|how r u|how are u)\b": "I'm just a bot, but I'm functioning well! How can I help?",
    r"(?i)\b(whats up|sup|wassup)\b": "Not much, just ready to answer your questions!",
    r"(?i)\b(gm|good morning|goog dmorng|goodmorning)\b": "Good morning! ☀️ How can I help you today?",
    r"(?i)\b(ga|good afternoon)\b": "Good afternoon! 🌞 What can I do for you?",
    r"(?i)\b(ge|good evening)\b": "Good evening! 🌙 How can I assist you?",
    r"(?i)\b(gn|good night|goodnight)\b": "Good night! 😴 Sleep well!",
    r"(?i)\b(bye|goodbye|see ya|cya)\b": "Goodbye! 👋 Have a great day!",
    r"(?i)\b(thank|thanks|thx|ty)\b": "You're welcome! 😊",
    r"(?i)^(?:whats )?app$": "I'm an AI assistant, not WhatsApp! How can I help?",
   # Appreciations
    r"(?i)^(thank|thanks|thx|ty|thank you|appreciate it)$": "You're welcome! 😊",
    
    # Name queries
    r"(?i)\b(what(?:'?s| is) your name\??)\b": "I'm  your AI assistant!",
    r"(?i)\b(who are you)\b": "I'm an AI assistant here to help answer your questions!",
    
    # WhatsApp confusion
    r"(?i)^(?:whats )?app$": "I'm an AI assistant, not WhatsApp! How can I help?",
    
    # Frustration/annoyance
    r"(?i)\b(annoying|frustrating|irritating|bothersome|snaniro)\b": "I'm sorry to hear that. I'll do my best to help!",
    r"(?i)\b(thase|that'?s)\b.*\b(well|good|fine)\b": "I'm here to help. Could you clarify what you mean?",
    
    # Generic responses
    r"(?i)^(ok|okay|k|alright|sure|got it)$": "Alright! How else can I assist?",
    r"(?i)^(cool|nice|awesome|great)$": "Glad to hear it! 😄 What can I do for you?",
}


def get_static_response(query: str) -> str:
    """Handle all types of static messages with priority matching"""
    # Normalize query: remove punctuation, extra spaces, and lowercase
    normalized = re.sub(r'[^\w\s]', '', query).strip().lower()
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # 1. Handle empty/special character queries
    if not normalized or re.fullmatch(r'[\s\W]+', query):
        return "I didn't catch that. Could you rephrase your question?"
    
    # 2. Handle very short queries (1-3 characters)
    if len(normalized) <= 3:
        for pattern, response in STATIC_RESPONSES.items():
            if re.fullmatch(pattern, normalized):
                return response
        return "Could you elaborate a bit more on that?"
    
    # 3. Check for exact matches in patterns
    for pattern, response in STATIC_RESPONSES.items():
        if re.fullmatch(pattern, normalized):
            return response
    
    # 4. Check for partial matches
    for pattern, response in STATIC_RESPONSES.items():
        if re.search(pattern, normalized):
            return response
    
    # 5. Handle gibberish/random strings
    if (len(normalized) < 10 and 
        not re.search(r'[aeiouy]', normalized) and 
        re.fullmatch(r'^[a-z]+$', normalized)):
        return "I'm not sure I understand. Could you try rephrasing your question?"
    
    return None

class RagQARequest(BaseModel):
    user_query: str
    session_id: str

@app.get("/fetch-data")
async def fetch_data():
    result = await fetch_and_save_data()
    return result

@app.post("/rag-qa")
def rag_qa(payload: RagQARequest):
    static_response = get_static_response(payload.user_query)
    if static_response:
        return {"answer": static_response}
    print(payload.user_query)
    config = {"configurable": {"thread_id": payload.session_id}}
    inputs = {"user_query": payload.user_query}
    result = workflow.invoke(inputs, config=config)
    return {"answer": result["final_answer"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
