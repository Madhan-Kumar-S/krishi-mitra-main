from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Add the backend directory to the Python path
sys.path.append(BACKEND_DIR)

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_google_credentials():
    """Setup Google Cloud credentials from environment variable"""
    creds_str = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_str:
        try:
            # If it's a JSON string, parse it and write to a temporary file
            creds = json.loads(creds_str)
            temp_creds_path = os.path.join(BACKEND_DIR, 'temp_creds.json')
            with open(temp_creds_path, 'w') as f:
                json.dump(creds, f)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_creds_path
            logger.info("Google credentials set up from environment variable")
        except json.JSONDecodeError:
            # If it's a file path, use it directly
            logger.info("Using Google credentials from file path")
    else:
        logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set")

# Setup Google credentials
setup_google_credentials()

# Import config
try:
    from configs.config import set_envs
    set_envs()
except ImportError as e:
    logger.error(f"Failed to import config: {e}")
    # Try to add the parent directory to the path
    try:
        sys.path.append(os.path.dirname(BACKEND_DIR))
        from configs.config import set_envs
        set_envs()
    except ImportError as e:
        logger.error(f"Failed to import config from alternative path: {e}")
        raise

# Now import the app components that need the credentials
from app import llm_svc, chroma, json_chain

app = FastAPI(title="KrishiMitra API")

# Configure CORS - Update this with your React Native app's domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your React Native app's domain
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
    try:
        # Process the query using the existing chain
        llm_response = json_chain.invoke({
            "query": f"""
            User Input: {query.text}
            Provide a JSON response with the following keys:
            * language: The language of the input text.
            * text: A proper English translation understandable by a native English speaker.
            * language_code: The equivalent Google Cloud Platform language code for text-to-speech.
            """
        })
        
        user_language = llm_response['language']
        user_input = llm_response['text']
        user_language_code = llm_response["language_code"]

        # Get relevant documents from Chroma
        docs = chroma.similarity_search(user_input)
        context = " ".join(doc.page_content for doc in docs[:4])

        if not context:
            raise HTTPException(status_code=404, detail="No relevant information found")

        # Generate response using the LLM
        prompt = f"""
        You are a highly knowledgeable assistant specializing in Indian government schemes. 
        Your task is to provide clear, accurate, and actionable information to users about various government programs 
        related to areas like education, healthcare, agriculture, and insurance. 
        Your responses should be grounded in the provided context and include details about the scheme name, specific benefits, and eligibility criteria. 
        Ensure the information is delivered in a straightforward, conversational manner without using markdown formatting.
        Example Query: {user_input}
        Context: {context}
        Answer in {user_language}. Language code: {user_language_code}.
        """

        response = llm_svc.get_llm().invoke(prompt)
        
        return Response(
            response=response.content,
            language=user_language,
            language_code=user_language_code
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port) 