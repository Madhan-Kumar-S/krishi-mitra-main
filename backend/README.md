# KrishiMitra Backend API

This is the FastAPI backend for the KrishiMitra application, which provides an API interface for the React Native mobile app to interact with the KrishiMitra core functionality.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure you have the Google Cloud credentials file (`krishimitra-457511-b14259bcb536.json`) in the root directory.

## Running the Server

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

### GET /
Welcome endpoint that returns a simple message.

### POST /query
Main endpoint for processing queries about government schemes.

Request body:
```json
{
    "text": "Tell me about the Garuda Scheme",
    "language": "english"  // optional
}
```

Response:
```json
{
    "response": "Detailed response about the scheme...",
    "language": "english",
    "language_code": "en-US"
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Successful response
- 404: No relevant information found
- 500: Internal server error

## CORS

CORS is enabled for all origins in development. For production, update the CORS settings in `main.py` to only allow requests from your React Native app's domain. 