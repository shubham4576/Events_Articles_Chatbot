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

class FetchRequest(BaseModel):
    start_date: date
    end_date: Optional[date] = date.today()

class RagQARequest(BaseModel):
    user_query: str
    session_id: str

@app.post("/fetch-data")
async def fetch_data(payload: FetchRequest):
    result = await fetch_and_save_data(
        start_date=str(payload.start_date),
        end_date=str(payload.end_date),
        json_file_path=str(BASE_PATH / "data" / "data.json")
    )
    return result

@app.post("/rag-qa")
def rag_qa(payload: RagQARequest):
    config = {"configurable": {"thread_id": payload.session_id}}
    inputs = {"user_query": payload.user_query}
    result = workflow.invoke(inputs, config=config)
    return {"answer": result["final_answer"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
