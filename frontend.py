import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

# NOTE: When we type enter in text box the whole scripts runs again

# *************************** Utility **************************************************

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    # reset the message history
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

# *************************** Session Setup **************************************************

# st.session_state ->  it is a dict where the data persists even if we enter in the text box 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state["thread_id"])

# *************************** Sidebar UI **************************************************

st.sidebar.title("Chatbot")

if st.sidebar.button("New chat"):
    reset_chat()

st.sidebar.header("Past Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        # For extracting the messages in our desired format
        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

# *************************** Main UI **************************************************

# load the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input('Type here')

if user_input:

    #  add the  user message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

    #  add assistant message to  message_history
    with st.chat_message('assistant'):
       ai_message = st.write_stream(
            message_chunk.content for  message_chunk, metadata in chatbot.stream(
                {
                    "messages": [HumanMessage(content=user_input)]
                },
                config=CONFIG,
                stream_mode="messages"
            )
        )
       
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
