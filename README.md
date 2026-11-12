# 🤖 MyAI – Intelligent Personal Assistant

**MyAI** is a personal AI assistant built with Python, Streamlit, Ollama, and SQLite. It helps users chat with AI, manage conversations, work with documents, and complete everyday text-based tasks.
## 🖥️ MyAI Application Screenshot

![MyAI Assistant](MyAI%20screenshot.png)

## ✨ Features

- **AI Chatbot:** Chat with a locally running AI model.
- **Persistent Memory:** Store conversations using SQLite.
- **Chat Management:** Create, rename, delete, and revisit conversations.
- **PDF Reader:** Upload and ask questions about PDF documents.
- **Web Search:** Search the web for additional information.
- **AI Calculator:** Perform mathematical calculations.
- **Personalization:** Customize the assistant using a personal profile.
- **Smart AI Tools:**
  - Text Summarizer
  - Language Translator
  - Email Writer
  - Notes Assistant

## 🛠️ Technologies Used

- Python
- Streamlit
- Ollama
- Qwen3 (1.7B)
- SQLite
- Git and GitHub

## 📋 Requirements

Before running MyAI, install:

1. Python
2. Ollama
3. Git (optional, for cloning and development)

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sanju4551/MyAI-Assistant-.git
cd MyAI-Assistant-
```

### 2. Create a virtual environment

```bash
py -m venv .venv
```

### 3. Activate the environment (Windows)

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Download the AI model

```bash
ollama pull qwen3:1.7b
```

Make sure Ollama is installed and running.

### 6. Run MyAI

```bash
python -m streamlit run app.py
```

Open this address in your browser:

http://localhost:8501

## 📁 Project Structure

```text
MyAI-Assistant/
│
├── app.py
├── calculator.py
├── database.py
├── profile.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🔒 Privacy

MyAI uses a local Ollama model for AI responses. Conversation history and personal profile data are stored locally.

Private files such as the database and personal profile are excluded from this GitHub repository.

## 👨‍💻 Author

**Sanjay**

GitHub: [@sanju4551](https://github.com/sanju4551)

## 📌 Project Status

MyAI is an ongoing learning and development project. New features and improvements will be added over time.

## 🚀 Future Improvements

- [ ] Improve voice interaction and microphone support.
- [ ] Enhance live web search and information retrieval.
- [ ] Deploy MyAI online for remote access.
- [ ] Add more AI-powered productivity tools.
- [ ] Improve the user interface and user experience.
- [ ] Add secure user authentication and multi-user support.
