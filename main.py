import streamlit as st
import json
from utils.lex_client import LexClient
from config.config import Config
from datetime import datetime

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'request_response_history' not in st.session_state:
        st.session_state.request_response_history = []
    if 'bot_id' not in st.session_state:
        st.session_state.bot_id = None
    if 'bot_alias_id' not in st.session_state:
        st.session_state.bot_alias_id = None

def render_header():
    st.markdown("""
        <style>
        .header-container {
            padding: 10px;
            background: white;
            border-bottom: 1px solid #ddd;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    config = Config()
    with col1:
        bot_id = st.text_input("Bot ID", value=config.BOT_ID, key="bot_id_input")
    with col2:
        bot_alias_id = st.text_input("Bot Alias ID", value=config.BOT_ALIAS_ID, key="bot_alias_input")
    with col3:
        if st.button("Update", use_container_width=True):
            st.session_state.bot_id = bot_id
            st.session_state.bot_alias_id = bot_alias_id
            st.success("Bot configuration updated!")

def render_debug_panel():
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            height: calc(100vh - 300px);
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### Request/Response History")
    debug_container = st.container()
    with debug_container:
        for entry in reversed(st.session_state.request_response_history):
            st.markdown(f"**Time: {entry['timestamp']}**")
            st.markdown("**Request:**")
            st.code(json.dumps(entry['request'], indent=2), language='json')
            st.markdown("**Response:**")
            st.code(json.dumps(entry['response'], indent=2), language='json')
            st.markdown("---")

def render_chat_interface(lex_client):
    st.markdown("""
        <style>
        /* Chat container styling */
        [data-testid="stChatMessageContent"] {
            overflow-wrap: break-word;
        }

        /* Chat input styling */
        .stChatFloatingInputContainer {
            position: sticky !important;
            bottom: 0 !important;
            background: white;
            padding: 10px 0;
            z-index: 100;
        }

        /* Chat messages container */
        .stChatMessageContent {
            max-height: calc(100vh - 300px);
            overflow-y: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### Chat Interface")

    # Chat messages
    for message in st.session_state.messages:
        timestamp = message.get("timestamp", "")
        with st.chat_message(message["role"]):
            st.markdown(f"**{timestamp}**")
            st.write(message["content"])

    # Input field
    user_input = st.chat_input("Type your message here...")

    if user_input:
        current_time = datetime.now().strftime("%H:%M:%S")

        # Immediately display user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": current_time
        })

        # Prepare request data
        request_data = {
            "botId": lex_client.bot_id,
            "botAliasId": lex_client.bot_alias_id,
            "localeId": lex_client.locale_id,
            "sessionId": "test-session",
            "text": user_input
        }

        # Get bot response
        response_data = lex_client.send_message(user_input)
        bot_response = response_data.get('messages', [{'content': 'No response'}])[0]['content']

        # Add to request/response history
        st.session_state.request_response_history.append({
            'timestamp': current_time,
            'request': request_data,
            'response': response_data
        })

        # Add bot response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        # Force refresh of chat container
        st.rerun()

def main():
    st.set_page_config(layout="wide")
    st.title("AWS Lex Chatbot")

    initialize_session_state()
    render_header()

    config = Config()
    lex_client = LexClient(config)

    if st.session_state.bot_id and st.session_state.bot_alias_id:
        lex_client.bot_id = st.session_state.bot_id
        lex_client.bot_alias_id = st.session_state.bot_alias_id

    col1, col2 = st.columns([1, 1])

    with col1:
        render_debug_panel()
    with col2:
        render_chat_interface(lex_client)

if __name__ == "__main__":
    main()
