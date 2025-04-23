from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="KrishiMitra API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str
    language: Optional[str] = None

class Response(BaseModel):
    response: str
    language: str
    language_code: str

@app.get("/")
async def root():
    return {"message": "Welcome to KrishiMitra API"}

@app.post("/query", response_model=Response)
async def process_query(query: Query):
    return Response(
        response="Test response",
        language="english",
        language_code="en-US"
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 


