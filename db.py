import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import sqlite3
import pandas as pd
import re

from langchain_groq import ChatGroq
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

load_dotenv()

# page config
st.set_page_config(
    page_title="SQL AI Assistant",
    page_icon="💻",
    layout="wide"
)

# custom css
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.block-container {
    padding-top: 2rem;
}

h1 {
    color: white;
    font-size: 42px;
    font-weight: 700;
}

.stTextInput > div > div > input {
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #374151;
}

.stChatInput input {
    border-radius: 12px;
}

.stButton button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    background-color: #2563EB;
    color: white;
    font-size: 15px;
    font-weight: 600;
    border: none;
}

.stButton button:hover {
    background-color: #1D4ED8;
    color: white;
}

.result-box {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #374151;
    margin-top: 10px;
}

.sql-box {
    background-color: #0B1220;
    padding: 15px;
    border-radius: 12px;
    border-left: 5px solid #2563EB;
    margin-top: 10px;
}

.sidebar-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# title
st.markdown(
    "<h1>Conversational SQL AI Assistant</h1>",
    unsafe_allow_html=True
)

# info section

with st.expander("✅ Read before connecting your MySQL database"):
    st.markdown("""


If you plan to connect your MySQL database, please ensure you have:

A public cloud MySQL host

A remotely accessible DB
    """)

st.markdown("""
Ask questions directly from your SQL database using natural language.
Supports SQLite and MySQL connections with AI-powered query generation.
""")

# database constants
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = [
    "Use SQLite (student.db)",
    "Connect to MySQL"
]

# sidebar
with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">Database Settings</div>',
        unsafe_allow_html=True
    )

    selected_opt = st.radio(
        "Choose Database",
        radio_opt
    )

    # MYSQL
    if radio_opt.index(selected_opt) == 1:

        db_uri = MYSQL

        mysql_host = st.text_input(
            "MySQL Host",
            value="127.0.0.1"
        )

        mysql_user = st.text_input(
            "MySQL User",
            value="root"
        )

        mysql_password = st.text_input(
            "MySQL Password",
            type="password"
        )

        mysql_database = st.text_input(
            "Database Name"
        )

    # SQLITE
    else:

        db_uri = LOCALDB

    st.markdown("---")

    api_key = st.text_input(
        "Groq API Key",
        type="password"
    )

    model_name = st.selectbox(
        "Choose Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ]
    )

    st.markdown("---")

    if st.button("Reset Database Cache"):

        st.cache_resource.clear()

        st.success("Database cache cleared")

    st.markdown("""
    ### Features

    - Natural Language to SQL
    - SQLite Support
    - MySQL Support
    - SQL Visualization
    - AI Query Explanation
    - Safe SQL Execution
    """)

    clear_chat = st.button("Clear Chat")

# api key validation
if not api_key:

    st.warning("Please enter your Groq API key")

    st.stop()

# llm initialization
try:

    model = ChatGroq(
        groq_api_key=api_key,
        model=model_name,
        streaming=True
    )

except Exception as e:

    st.error(f"Model Error: {e}")

    st.stop()

# database configuration
@st.cache_resource(ttl=0)
def configure_db(
    db_uri,
    mysql_host=None,
    mysql_user=None,
    mysql_password=None,
    mysql_database=None
):

    # SQLITE
    if db_uri == LOCALDB:

        dbfilepath = (
            Path(__file__).parent / "student.db"
        ).absolute()

        creator = lambda: sqlite3.connect(
            f"file:{dbfilepath}?mode=ro",
            uri=True
        )

        return SQLDatabase(
            create_engine(
                "sqlite:///",
                creator=creator
            )
        )

    # MYSQL
    elif db_uri == MYSQL:

        if not (
            mysql_host and
            mysql_user and
            mysql_password and
            mysql_database
        ):

            st.error(
                "Please enter all MySQL credentials"
            )

            st.stop()

        encoded_password = quote_plus(mysql_password)

        connection_string = (
            f"mysql+mysqlconnector://"
            f"{mysql_user}:{encoded_password}"
            f"@{mysql_host}/{mysql_database}"
        )

        return SQLDatabase.from_uri(
            connection_string
        )

# database initialization
try:

    if db_uri == MYSQL:

        db = configure_db(
            db_uri,
            mysql_host,
            mysql_user,
            mysql_password,
            mysql_database
        )

    else:

        db = configure_db(db_uri)

except Exception as e:

    st.error(f"Database Connection Error: {e}")

    st.stop()

# toolkit
toolkit = SQLDatabaseToolkit(
    db=db,
    llm=model
)

# custom prompt
prefix = """
You are an expert SQL assistant.

Rules:
- Generate safe SQL queries only
- Never generate DELETE, DROP, INSERT, UPDATE, ALTER, TRUNCATE
- Return concise answers
- If user asks for table format, return markdown table
"""

# sql agent
agent = create_sql_agent(
    llm=model,
    toolkit=toolkit,
    verbose=False,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    max_iterations=15,
    prefix=prefix
)

# chat history
if "messages" not in st.session_state or clear_chat:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "How can I help you?"
        }
    ]

# display previous messages
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(
            f"""
            <div class="result-box">
            {msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# sql extractor
def extract_sql(text):

    patterns = [
        r"(SELECT[\s\S]*?;)",
        r"(WITH[\s\S]*?;)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None

# user input
user_query = st.chat_input(
    "Ask a question about your database"
)

if user_query:

    # security restriction
    forbidden = [
        "delete",
        "drop",
        "truncate",
        "update",
        "insert",
        "alter"
    ]

    if any(
        word in user_query.lower()
        for word in forbidden
    ):

        st.warning(
            "Restricted database operation detected"
        )

        st.stop()

    # store user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    # display user message
    with st.chat_message("user"):

        st.markdown(
            f"""
            <div class="result-box">
            {user_query}
            </div>
            """,
            unsafe_allow_html=True
        )

    # assistant response
    with st.chat_message("assistant"):

        output = ""

        with st.spinner(
            "Generating SQL response..."
        ):

            try:

                response = agent.invoke(
                    {"input": user_query}
                )

                output = response.get(
                    "output",
                    "No response generated"
                )

                st.markdown(
                    f"""
                    <div class="result-box">
                    {output}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # extract sql query
                sql_query = extract_sql(output)

                if sql_query:

                    # additional sql protection
                    dangerous_keywords = [
                        "DELETE",
                        "DROP",
                        "TRUNCATE",
                        "ALTER",
                        "UPDATE",
                        "INSERT"
                    ]

                    upper_sql = sql_query.upper()

                    if any(
                        word in upper_sql
                        for word in dangerous_keywords
                    ):

                        st.error(
                            "Dangerous SQL detected"
                        )

                        st.stop()

                    st.subheader(
                        "Generated SQL Query"
                    )

                    st.markdown(
                        f"""
                        <div class="sql-box">
                        <pre>{sql_query}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # execute sql
                    try:

                        result = db.run(sql_query)

                        # display raw result
                        st.subheader("Query Result")

                        st.code(str(result))

                        # dataframe visualization
                        if not isinstance(result, str):

                            df = pd.DataFrame(result)

                            if not df.empty:

                                st.dataframe(df)

                                numeric_df = df.select_dtypes(
                                    include="number"
                                )

                                if not numeric_df.empty:

                                    st.markdown(
                                        "### Data Visualization"
                                    )

                                    st.bar_chart(numeric_df)

                    except Exception as viz_error:

                        st.warning(
                            f"Visualization Error: {viz_error}"
                        )

                    # explain query
                    if st.button(
                        "Explain This Query"
                    ):

                        explanation = model.invoke(
                            f"Explain this SQL query in simple terms:\n{sql_query}"
                        )

                        st.info(
                            explanation.content
                        )

            except Exception as e:

                output = f"Error: {str(e)}"

                st.error(output)

        # store assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": output
            }
        )