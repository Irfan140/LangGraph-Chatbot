import streamlit as st
from backend import chatbot, retrieve_all_threads
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

def generate_title(user_input):
    title_prompt = f"Generate a very short title (max 5 words) for a conversation that starts with this message: '{user_input}'. Reply with ONLY the title, no punctuation, no quotes."
    
    response = chatbot.invoke(
        {"messages": [HumanMessage(content=title_prompt)]},
        config={"configurable": {"thread_id": "title-gen"}}  # isolated thread so it doesn't pollute history
    )
    
    return response["messages"][-1].content.strip()

# *************************** Session Setup **************************************************

# st.session_state ->  it is a dict where the data persists even if we enter in the text box 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}
    
    # Re-derive titles for all threads loaded from DB
    for thread_id in st.session_state["chat_threads"]:
        thread_id_str = str(thread_id)
        if thread_id_str not in st.session_state["chat_titles"]:
            messages = load_conversation(thread_id)
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    title = generate_title(msg.content)
                    st.session_state["chat_titles"][thread_id_str] = title
                    break

add_thread(st.session_state["thread_id"])

# *************************** Sidebar UI **************************************************

st.sidebar.title("Chatbot")

if st.sidebar.button("New chat"):
    reset_chat()

st.sidebar.header("Past Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    thread_id_str = str(thread_id)
    title = st.session_state["chat_titles"].get(thread_id_str, "New Chat")

    if st.sidebar.button(title, key=thread_id_str):
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
        st.markdown(message['content'])


user_input = st.chat_input('Type here')

if user_input:

    #  add the  user message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    #  Generate title only on first message of this thread
    thread_id_str = str(st.session_state["thread_id"])
    if thread_id_str not in st.session_state["chat_titles"]:
        title = generate_title(user_input)
        st.session_state["chat_titles"][thread_id_str] = title

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
