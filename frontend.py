import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

# NOTE: When we type enter in text box the whole scripts runs again

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# st.session_state ->  it is a dict where the data persists even if we enter in the text box 
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

#{'role': 'user', 'content': 'Hi'}
#{'role': 'assistant', 'content': 'Hello'}

user_input = st.chat_input('Type here')

if user_input:

    #  add the  user message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)


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
