from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGroq(model="moonshotai/kimi-k2-instruct-0905")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Node implementation
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# creating db
connection = sqlite3.connect(database="chatbot.db", check_same_thread=False) # doing so as sqlite3 only can work for a single thread

# Checkpointer
checkpointer = SqliteSaver(conn=connection)

# Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    # checkpointer.list(None) means get me all the checkpoints
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        if thread_id != "title-gen":  # ← exclude internal title thread
            all_threads.add(thread_id)
    return list(all_threads)