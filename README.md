# 🔍 Source Code Analyzer

> **AI-powered codebase exploration using Retrieval-Augmented Generation (RAG)**

Ask natural-language questions about any public GitHub repository. The system clones the repo, indexes all Python source files into a vector store, and answers questions using Groq Llama 3.3 70B with conversational memory — entirely free to run.

---

## 📸 Demo

![System Architecture](Generated_image342423.png)

---

## ✨ Features

- 🤖 **Natural Language Q&A** — Ask plain-English questions about any Python codebase
- 🔁 **Conversational Memory** — Follow-up questions retain context from previous answers
- ⚡ **Fast Inference** — Groq's LPU delivers low-latency responses with Llama 3.3 70B
- 🆓 **100% Free Stack** — Groq (free tier) + HuggingFace embeddings (local CPU) + ChromaDB (local)
- 🌐 **Web Interface** — Clean browser UI, no CLI required
- 📎 **Source References** — Every answer cites the relevant source files

---

## 🏗️ System Architecture

### Ingestion Phase *(runs once per repository)*

```
GitHub Repo
    │
    ▼
[Clone with GitPython]
    │
    ▼
[Load all .py files with LangChain DirectoryLoader]
    │
    ▼
[Split into 1000-char chunks with 200-char overlap]
 (splits at class/function boundaries when possible)
    │
    ▼
[Convert each chunk → 384-dimensional vector]
 (HuggingFace all-MiniLM-L6-v2, runs on CPU)
    │
    ▼
[Store vectors + text + metadata in ChromaDB]
 (persisted to disk in db/ directory)
```

### Query Phase *(runs on every question)*

```
User Question: "What does the main function do?"
    │
    ▼
[Embed question using same HuggingFace model]
    │
    ▼
[Search ChromaDB — top 6 most similar code chunks]
    │
    ▼
[Build prompt: system + chat history + code context + question]
    │
    ▼
[Send to Groq Llama 3.3 70B]
    │
    ▼
[Return answer + source file references]
[Save Q&A to history for follow-up questions]
```

### Key Parameters

| Parameter | Value | Reason |
|-----------|-------|--------|
| Chunk Size | 1000 characters | Balances context with retrieval precision |
| Chunk Overlap | 200 characters | Prevents function signatures being cut off |
| Retrieval K | 6 chunks | Enough context without exceeding token limits |
| Temperature | 0.2 | Precise, factual answers |
| Max Tokens | 2000 | Detailed responses within limits |
| Chat Memory | Last 6 pairs | Maintains follow-up context efficiently |

---

## 📁 Project Structure

```
source-code-analyzer/
├── app.py                  # Flask web server (main entry point)
├── ingest.py               # Repository ingestion pipeline
├── chat.py                 # RAG conversation engine
├── requirements.txt        # Python package dependencies
├── .env                    # API key configuration (not committed to git)
├── generate_ppt.py         # PowerPoint presentation generator
├── README.md               # This file
│
├── templates/
│   └── index.html          # Web interface (HTML)
│
├── static/
│   ├── css/
│   │   └── style.css       # Application styling
│   └── js/
│       └── app.js          # Frontend logic
│
├── repo/                   # Cloned repositories (auto-created)
├── db/                     # ChromaDB vector store (auto-created)
└── venv/                   # Python virtual environment
```

---

## 🛠️ Installation

### Prerequisites

| Tool | Version | Link |
|------|---------|------|
| Python | 3.10+ | https://python.org |
| Git | Any | https://git-scm.com |
| Groq API Key | Free | https://console.groq.com |

### Step-by-Step Setup

```bash
# 1. Clone this repository
git clone https://github.com/your-username/source-code-analyzer.git
cd source-code-analyzer

# 2. Create & activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
# (Takes 5–10 min — downloads PyTorch + AI model on first run)

# 4. Configure your API key
# Create a .env file with:
echo "GROQ_API_KEY=gsk_your-key-here" > .env

# 5. Run the application
python app.py
```

Then open your browser at: **http://localhost:5000**

### Verify Installation

```bash
python -c "
from flask import Flask
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
print('All packages installed correctly!')
"
```

---

## 🚀 Usage

### 1. Analyze a Repository

1. Paste a GitHub URL in the top input field  
2. Click **"Analyze Repository"**  
3. Wait 1–3 minutes (progress shown in terminal)  

**Recommended test repos (small & fast):**
```
https://github.com/dbader/schedule         (~5 Python files)
https://github.com/realpython/reader       (~10 Python files)
```

### 2. Ask Questions

Once ingestion completes, type questions in the chat input:

```
"What does this project do?"
"What are the main classes and functions?"
"Explain how the scheduling mechanism works"
"What dependencies does this project use?"
"Show me the entry point of the application"
"Are there any potential bugs in the code?"
```

### 3. Follow-Up Questions

The system remembers previous exchanges:

```
You:  "What are the main classes?"
Bot:  "The main classes are Scheduler, Job, ..."

You:  "Tell me more about the Scheduler class"
Bot:  "The Scheduler class is responsible for..."  ← remembers context
```

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| `GET` | `/` | Serve web UI | — | HTML page |
| `POST` | `/chatbot` | Ingest repository | `msg`: GitHub URL | `{"response": "..."}` |
| `GET` | `/get` | Ask a question | `msg`: question text | `{"response": "..."}` |

**cURL examples:**

```bash
# Ingest a repository
curl -X POST http://localhost:5000/chatbot \
  -d "msg=https://github.com/dbader/schedule"

# Ask a question
curl "http://localhost:5000/get?msg=What%20does%20this%20project%20do"
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `Flask` | Web server framework |
| `python-dotenv` | Load `.env` variables |
| `gitpython` | Clone GitHub repositories |
| `langchain` | AI orchestration framework |
| `langchain-community` | Document loaders |
| `langchain-groq` | Groq LLM integration |
| `langchain-huggingface` | HuggingFace embedding integration |
| `langchain-chroma` | ChromaDB vector store integration |
| `chromadb` | Vector database |
| `sentence-transformers` | Local embedding model runtime |

---

## ⚙️ Configuration

All key parameters can be tuned directly in the source files:

| File | Parameter | Default | Description |
|------|-----------|---------|-------------|
| `ingest.py` | `CHUNK_SIZE` | `1000` | Characters per code chunk |
| `ingest.py` | `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `ingest.py` | `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model name |
| `chat.py` | `k` | `6` | Chunks retrieved per question |
| `chat.py` | `model_name` | `llama-3.3-70b-versatile` | Groq LLM model |
| `chat.py` | `temperature` | `0.2` | 0 = precise, 1 = creative |
| `chat.py` | `max_tokens` | `2000` | Max response length |
| `chat.py` | `_chat_history[-6:]` | Last 6 | Q&A pairs kept in memory |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `GROQ_API_KEY not found` | Check `.env` exists with `GROQ_API_KEY=gsk_...` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv activated |
| Repository clone failed | Ensure URL starts with `https://github.com/` and repo is public |
| No Python files found | The repository doesn't contain `.py` files |
| `429 Rate limit` | Wait 60 seconds — free tier allows 30 requests/minute |
| Port 5000 in use | Change port in `app.py`: `app.run(port=8080)` |
| Slow first run | Normal — downloads 90MB embedding model once |
| venv creation fails | Try `python -m venv venv --without-pip`, then install pip manually |

---

## 🔭 Future Scope

- **Multi-Language Support** — Extend beyond Python to JavaScript, Java, Go, Rust, C++
- **Code Visualization** — Generate dependency graphs and architecture diagrams
- **Bug Detection** — AI-powered vulnerability and code quality scanning
- **Auto Documentation** — Generate README and API docs from code
- **Private Repos** — GitHub OAuth for private repository access
- **Cloud Deployment** — Deploy on AWS/GCP with multi-user support
- **IDE Extension** — VS Code plugin for in-editor code analysis
- **Code Comparison** — Diff and compare two repositories or branches

---

## 📚 References

- Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS.
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)

---

## 🧑‍💻 Built With

**Flask** · **LangChain** · **ChromaDB** · **Groq Llama 3.3 70B** · **HuggingFace Embeddings**

---

*Free to use. No paid APIs required beyond the free Groq tier.*
