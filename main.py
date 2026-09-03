import uuid
from config import get_ai_model
import database as db

def main():
    # 1. Initialize the local database file structure
    db.init_db()
    
    # 2. Establish a unique session ID for this conversation instance
    session_id = str(uuid.uuid4())[:8] 
    db.create_session(session_id)
    
    # 3. Pull previous history data from SQLite and initialize Buddy AI
    db_history = db.load_chat_history(session_id)
    model = get_ai_model()
    chat = model.start_chat(history=db_history)
    
    print("=================================================================")
    print(f"Buddy AI Chatbot Active (Session ID: {session_id})")
    print("Disclaimer: I am your Buddy, an AI helper, not a licensed professional.")
    print("Type 'exit' to end your session safely.")
    print("=================================================================\n")
    
    while True:
        user_input = input("You: ").strip()
        
        # Skip empty inputs
        if not user_input:
            continue
            
        # Graceful exit keywords
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nBuddy: Thank you for sharing today. Take care of yourself. Goodbye!")
            break
        
        # Log user text safely to local storage
        db.log_message(session_id, "User", user_input)
        
        try:
            # Deliver context stream to Gemini and receive generation text
            response = chat.send_message(user_input)
            bot_reply = response.text
            
            print(f"\nBuddy: {bot_reply}\n")
            
            # Log response text to local storage
            db.log_message(session_id, "Bot", bot_reply)
            
        except Exception as e:
            error_msg = f"I had a little trouble connecting. Can you try that again? (Error: {e})"
            print(f"\nBuddy: {error_msg}\n")

if __name__ == "__main__":
    main()
