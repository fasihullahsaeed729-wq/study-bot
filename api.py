from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from database import save_message, get_conversation_history
from typing import Optional
import uvicorn

load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Study Bot API", description="AI Study Assistant with Memory")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

# Request/Response Models
class ChatRequest(BaseModel):
    user_id: str
    question: str
    clear_history: Optional[bool] = False

class ChatResponse(BaseModel):
    user_id: str
    question: str
    answer: str
    history_length: int

class HistoryRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 10

# System prompt for study bot
SYSTEM_PROMPT = """You are a helpful Study Assistant bot. You help students with:
- Academic questions in all subjects (Math, Science, History, Literature, etc.)
- Study tips and techniques (time management, note-taking, exam preparation)
- Explanations of concepts (break down complex topics)
- Homework help (guide students to find answers themselves)

Remember what the student has asked before and reference previous conversations.
Be encouraging, patient, and educational in your responses."""

def create_chain():
    """Create the LangChain with history support"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{question}")
    ])
    return prompt | llm

@app.get("/")
async def root():
    return {
        "message": "Welcome to Study Bot API",
        "version": "1.0",
        "endpoints": {
            "/chat": "POST - Chat with the study bot",
            "/history/{user_id}": "GET - Get user chat history",
            "/docs": "Swagger documentation"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with memory"""
    try:
        # Clear history if requested
        if request.clear_history:
            from database import clear_user_history
            clear_user_history(request.user_id)
        
        # Get conversation history
        history = get_conversation_history(request.user_id)
        
        # Create chain and get response
        chain = create_chain()
        response = chain.invoke({
            "history": history,
            "question": request.question
        })
        
        # Save to database
        save_message(request.user_id, "user", request.question)
        save_message(request.user_id, "assistant", response.content)
        
        return ChatResponse(
            user_id=request.user_id,
            question=request.question,
            answer=response.content,
            history_length=len(history) // 2  # Number of exchanges
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 10):
    """Get conversation history for a user"""
    try:
        history = get_conversation_history(user_id)
        
        # Format for display
        formatted_history = []
        for role, message in history[-limit*2:]:  # Limit exchanges
            formatted_history.append({
                "role": role,
                "message": message
            })
        
        return {
            "user_id": user_id,
            "history": formatted_history,
            "total_messages": len(history)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/history/{user_id}")
async def clear_history(user_id: str):
    """Clear all history for a user"""
    try:
        from database import clear_user_history
        count = clear_user_history(user_id)
        return {
            "message": f"Cleared {count} messages for user {user_id}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)