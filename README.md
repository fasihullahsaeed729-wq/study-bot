# Study Bot - AI Study Assistant

An AI-powered study assistant chatbot with memory using MongoDB.

## Features
- 📚 Answer study-related questions
- 🧠 Remembers conversation history per user
- 💬 Context-aware responses
- 🚀 Deployed as FastAPI

## API Endpoints
- `GET /` - Welcome message
- `POST /chat` - Chat with the bot
- `GET /history/{user_id}` - Get user history
- `DELETE /history/{user_id}` - Clear history

## Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with API keys
5. Run: `python api.py`

## Technologies Used
- FastAPI
- MongoDB
- LangChain
- Groq LLM