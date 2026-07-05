# 🚀 DevPulse

> An AI-powered developer assistant that helps developers understand, analyze, and interact with software projects using Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and Model Context Protocol (MCP).

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Vite-61DAFB)
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Overview

DevPulse is an AI-powered developer assistant designed to improve software development productivity by enabling developers to ask natural language questions about their projects.

Instead of manually searching through hundreds of files, developers can simply ask questions like:

- "How does authentication work?"
- "Explain this API endpoint."
- "Where is the database connection created?"
- "What does this function do?"
- "Generate documentation for this module."

DevPulse combines Large Language Models with Retrieval-Augmented Generation (RAG) to understand project source code and provide context-aware responses.

---

# ✨ Features

- 🤖 AI-powered code understanding
- 📂 Repository indexing
- 🔍 Semantic code search
- 🧠 Context-aware responses using RAG
- 📑 Automatic documentation generation
- 💬 Interactive AI chat interface
- ⚡ FastAPI backend
- 🎨 Modern React frontend
- 🗂️ Vector search using FAISS
- 🔌 MCP Server support
- 📈 Scalable architecture

---

# 🏗️ Architecture

```
                User
                  │
                  ▼
          React Frontend
                  │
        REST API / WebSocket
                  │
                  ▼
            FastAPI Backend
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
   LangChain RAG         MCP Server
        │
        ▼
 Document Loader
        │
        ▼
 Text Splitter
        │
        ▼
 Google Embeddings
        │
        ▼
     FAISS Index
        │
        ▼
 Gemini LLM
        │
        ▼
   AI Generated Response
```

---

# 🛠 Tech Stack

## Frontend

- React
- Vite
- JavaScript
- HTML
- CSS

## Backend

- FastAPI
- Python
- Uvicorn

## AI Stack

- Google Gemini
- LangChain
- LangChain Community
- Google Generative AI Embeddings

## Vector Database

- FAISS

## Protocol

- MCP (Model Context Protocol)

## Other Libraries

- Pydantic
- dotenv
- pathlib
- os
- logging

---

# 📁 Project Structure

```
DevPulse/

│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── rag/
│   ├── mcp/
│   ├── vectorstore/
│   ├── uploads/
│   ├── app.py
│   └── requirements.txt
│
├── README.md
└── .env
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/allenbersho/Devpulse.git

cd Devpulse
```

---

## Backend Setup

Create a virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Environment Variables

Create a `.env` file

```env
GOOGLE_API_KEY=your_google_api_key

MODEL_NAME=gemini-2.5-flash

EMBEDDING_MODEL=models/text-embedding-004
```

---

# ▶️ Running the Project

Backend

```bash
uvicorn api.app:app --reload
```

Frontend

```bash
npm run dev
```

---

# 💡 Example Queries

The AI assistant can answer questions such as:

```
Explain this project.

How does authentication work?

Generate documentation for this module.

Where is the database connection?

Explain the API flow.

What files are responsible for user login?

Summarize this repository.

Find all API endpoints.
```

---

# 🧠 How It Works

1. User uploads or connects a project.
2. Source files are loaded.
3. Files are split into chunks.
4. Chunks are converted into embeddings.
5. Embeddings are stored in FAISS.
6. User asks a question.
7. Relevant chunks are retrieved.
8. Gemini receives the context.
9. AI generates an accurate answer.

---

# 🔄 Workflow

```
Project Files
      │
      ▼
Document Loader
      │
      ▼
Text Splitter
      │
      ▼
Embeddings
      │
      ▼
FAISS Vector Store
      │
      ▼
Retriever
      │
      ▼
Gemini LLM
      │
      ▼
Response
```

---

# 🎯 Future Improvements

- Multi-repository support
- GitHub integration
- Pull Request review
- Code quality analysis
- Bug detection
- CI/CD integration
- Team collaboration
- Docker deployment
- Authentication
- Conversation history
- Voice interaction
- Multi-agent architecture

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```
git checkout -b feature-name
```

3. Commit your changes

```
git commit -m "Added new feature"
```

4. Push

```
git push origin feature-name
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Allen Bersho A P**

- GitHub: https://github.com/allenbersho

---

## ⭐ If you found this project useful, consider giving it a star on GitHub!
