import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from database import save_message, get_conversation_history

load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

def create_study_chain():
    """Create the study bot chain with memory support"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful Study Assistant bot. You help students with:
         - Academic questions in all subjects (Math, Science, History, Literature, etc.)
         - Study tips and techniques (time management, note-taking, exam preparation)
         - Explanations of concepts (break down complex topics)
         - Homework help (guide students to find answers themselves)
         
         Remember what the student has asked before and reference previous conversations.
         Be encouraging, patient, and educational in your responses."""),
        
        # This placeholder will be filled with conversation history
        MessagesPlaceholder(variable_name="history"),
        
        ("user", "{question}")
    ])
    
    return prompt | llm

def chat_with_memory():
    """Chatbot with memory functionality"""
    print("📚 Study Bot with Memory initialized!")
    print("Type 'quit' to exit, 'clear' to reset your history.\n")
    
    # Get user identifier
    user_id = input("Enter your name (for personalized memory): ").strip()
    if not user_id:
        user_id = "anonymous_user"
    
    # Create chain
    chain = create_study_chain()
    
    while True:
        user_input = input(f"\n{user_id}: ")
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            from database import clear_user_history
            count = clear_user_history(user_id)
            print(f"🧹 Cleared {count} messages from your history")
            continue
        
        # Get conversation history
        history = get_conversation_history(user_id)
        
        # Get bot response
        response = chain.invoke({
            "history": history,
            "question": user_input
        })
        
        # Save to database
        save_message(user_id, "user", user_input)
        save_message(user_id, "assistant", response.content)
        
        # Display response
        print(f"\n📖 Study Bot: {response.content}")

if __name__ == "__main__":
    chat_with_memory()