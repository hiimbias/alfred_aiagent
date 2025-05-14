from app.components.agent import JARVIS_AGENT
from app.components.services.auth import authenticate
from app.components.exceptions import AuthenticationError
import json
import streamlit as st

def main():
    st.set_page_config(page_title="Jarvis Chatbot", page_icon="🤖")
    st.title("🤖 Jarvis Chatbot")
    st.write("Talk to Jarvis, your personal assistant!")

    # Authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username=username, password=password):
                st.success("Authentication successful!")
                st.session_state.authenticated = True
                st.session_state.chat_history = []
            else:
                st.error("Invalid credentials.")
        return

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history with alternating bubbles
    for sender, message in st.session_state.chat_history:
        with st.chat_message("user" if sender == "You" else "assistant"):
            st.markdown(message)

    # Input field
    user_input = st.chat_input("Type your message...")
    if user_input:
        # Append user's message
        st.session_state.chat_history.append(("You", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            generator = JARVIS_AGENT.execute(messages=[
                {"role": "user", "content": user_input}
            ])

            # Append assistant's responses one-by-one in the same order
            for response in generator:
                if response.content:
                    st.session_state.chat_history.append(("Jarvis", response.content))
                    with st.chat_message("assistant"):
                        st.markdown(response.content)

        except AuthenticationError as e:
            st.error(f"Authentication failed: {e}")
            st.session_state.authenticated = False
            return

    # Save conversation
    if st.button("Save & Exit"):
        history = JARVIS_AGENT.get_history()
        with open("conversation_history.json", "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        st.success("Conversation saved. Thank you!")
        st.session_state.authenticated = False
        st.rerun()

if __name__ == "__main__":
    main()
