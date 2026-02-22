from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
db = client['study_bot_db']
collection = db['conversations']

def save_message(user_id, role, message):
    """Save a message to MongoDB"""
    document = {
        "user_id": user_id,
        "role": role,  # 'user' or 'assistant'
        "message": message,
        "timestamp": datetime.now()
    }
    collection.insert_one(document)
    print(f"✅ Saved {role} message for user {user_id}")

def get_conversation_history(user_id, limit=10):
    """Get recent conversation history for a user"""
    history = collection.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit)
    
    # Convert to list and reverse to get chronological order
    messages = list(history)
    messages.reverse()
    
    # Format for LangChain
    formatted_history = []
    for msg in messages:
        formatted_history.append((msg["role"], msg["message"]))
    
    return formatted_history

def clear_user_history(user_id):
    """Clear all history for a user (optional)"""
    result = collection.delete_many({"user_id": user_id})
    return result.deleted_count