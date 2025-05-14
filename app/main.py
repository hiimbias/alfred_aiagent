from app.core.agent import JARVIS_AGENT
from app.core.services.auth import authenticate
from app.core.exceptions import AuthenticationError
import json

import streamlit as st

def chat_loop():
    while True:
        try: 
            user_input = st.text_input("You: ", "")
            
            if user_input.lower() in ("exit", "quit", "bye"):
                history = JARVIS_AGENT.get_history()
                file_name = "conversation_history.json"
                
                with open(file_name, "w") as f:
                    json.dump(history, f, ensure_ascii=False, indent=4)
                st.success(f"Conversation history saved to {file_name}.")
                st.write("Thank you for talking to Jarvis! Goodbye!")
                break
                    
                    
            if user_input:
                response = JARVIS_AGENT.execute(user_input)
                st.text_area("Jarvis: ", value=response, height=300)
                st.text_input("You: ", "")
        except AuthenticationError as e:
            st.error(f"Authentication failed: {e}")
            break
        
def main():
    st.title("Jarvis Chatbot")
    st.write("Talk to Jarvis, your personal assistant!")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Authentication
    if not authenticate(username = username, password = password):
        st.error("Authentication error: Invalid credentials. Please try again.")
        return
    else:
        st.success("Authentication successful! You can now chat with Jarvis.")
        
    # Chat loop
    chat_loop()
    
if __name__ == "__main__":
    main()