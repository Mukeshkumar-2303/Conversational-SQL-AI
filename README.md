# 🧠 Conversational AI System for Querying SQL Databases

This project is a **Streamlit-based AI chatbot** that allows users to interact with SQL databases using **natural language queries**. It uses **LangChain agents** and **Groq LLM (LLaMA 3)** to convert user questions into SQL queries and fetch results.

---

## 🚀 Features

* 💬 Chat with your database using natural language
* 🗄️ Supports multiple databases:

  * SQLite (preloaded sample database)
  * MySQL (user-provided database connection)
* 🔐 Users can **enter their own MySQL credentials** (host, username, password, database)
* ⚡ Powered by Groq LLM (LLaMA 3)
* 🔗 Built using LangChain SQL Agent
* 📊 Interactive Streamlit chat interface
* 🧠 Automatic SQL query generation

---

## 🏗️ Project Structure

```id="p7s2ak"
├── db.py               # Main Streamlit application
├── sqlite.py           # Script to create and populate SQLite DB
├── student.db          # Sample SQLite database
├── .env                # Environment variables (API keys)
├── requirements.txt    # Dependencies
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash id="t7cs7z"
git clone https://github.com/your-username/streamlit-sql-ai-assistant.git
cd streamlit-sql-ai-assistant
```

### 2. Create virtual environment

```bash id="w6c5sk"
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash id="6w2u1k"
pip install -r requirements.txt
```

---

## 🔑 Setup Environment Variables

Create a `.env` file:

```id="6sz0k7"
GROQ_API_KEY=your_groq_api_key
```

---

## 🗄️ Database Setup

### 🔹 Option 1: SQLite (Default)

Run the script to create the sample database:

```bash id="1ep4v7"
python sqlite.py
```

This creates a `student.db` file with sample records.

---

### 🔹 Option 2: Connect Your Own MySQL Database ✅

You can connect your **own SQL database directly from the app UI**.

In the Streamlit sidebar, enter:

* **MySQL Host** → e.g. `localhost`
* **MySQL User** → e.g. `root`
* **MySQL Password**
* **Database Name**

👉 No need to modify code — just enter credentials in the UI.

---

## ▶️ Run the Application

```bash id="h7sd0m"
streamlit run db.py
```

---

## 💡 How It Works

1. Enter your **Groq API Key**
2. Choose database type:

   * SQLite (local sample)
   * MySQL (your own database)
3. Ask questions in natural language

The system will:

* Convert your question → SQL query
* Execute query on your database
* Return results in chat format

---

## 🧪 Example Queries

```id="j1l9od"
Show all students
```

```id="q5d6np"
Who scored more than 90?
```

```id="v9r3bc"
List all records from my table
```

```id="d4n8ks"
Count number of users in database
```

---

## 🔐 Security Note

* Your database credentials are **not stored permanently**
* Used only during the session
* Avoid connecting to sensitive production databases

---

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **LLM**: Groq (LLaMA 3)
* **Framework**: LangChain
* **Database**: SQLite / MySQL
* **Connector**: SQLAlchemy

---

## 📌 Future Improvements

* PostgreSQL support
* Authentication system
* Data visualization (charts)
* Upload custom datasets

---

## 🤝 Contributing

Pull requests are welcome. Open an issue for major changes.

---

## 📜 License

MIT License

---

## 🙌 Acknowledgements

* LangChain
* Groq API
* Streamlit
