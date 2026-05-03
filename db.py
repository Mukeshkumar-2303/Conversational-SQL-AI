import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
import sqlite3

from langchain_groq import ChatGroq
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Conversational AI System for Querying SQL Databases Using LangChain",
    page_icon=""
)

st.title("Conversational AI System for Querying SQL Databases Using LangChain")

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLLITE 3 Database- student.db", "connect to you SQL Database"]

selected_opt = st.sidebar.radio(
    label="choose the DB which you want to chat with",
    options=radio_opt
)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input(" My SQL Host")
    mysql_user = st.sidebar.text_input(" My SQL user")
    mysql_password = st.sidebar.text_input(" My SQL user password")
    mysql_database = st.sidebar.text_input(" My SQL Database name")
else:
    db_uri = LOCALDB

api_key = st.sidebar.text_input(label="Groq api key", type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please enter the api key")

# LLM MODEL
model = ChatGroq(
    groq_api_key=api_key,
    model="llama-3.3-70b-versatile",
    streaming=True
)

@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_database=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_password and mysql_database and mysql_user):
            st.error("please enter all the database credentials")
            st.stop()

        return SQLDatabase.from_uri(
            f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
        )

if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_database)
else:
    db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=model)

# agent
agent = create_sql_agent(
    llm=model,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Chat history
if "messages" not in st.session_state or st.sidebar.button("clear message history"):
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_query = st.chat_input(placeholder="Ask a question about your database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())

        try:
            response = agent.invoke(
                {"input": user_query},
                callbacks=[streamlit_callback]
            )

            output = response["output"]

        except Exception as e:
            output = f"Error: {str(e)}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": output
        })

        st.write(output)
