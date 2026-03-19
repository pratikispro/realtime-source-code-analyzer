# Source Code Analyzer

A generative AI-powered web application that lets you point any public GitHub repository at the system and ask natural-language questions about its codebase. The system clones the repository, indexes Python source files into a vector store, and answers questions using Retrieval-Augmented Generation (RAG) with conversational memory.

![System Architecture](./asset/system-architecture.png)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | Flask |
| LLM | Groq Llama 3.3 70B |
| Embeddings | HuggingFace all-MiniLM-L6-v2 (local CPU) |
| Vector Store | ChromaDB |
| AI Orchestration | LangChain |
| Repo Cloning | GitPython |

---

## How It Works

**Ingestion** (once per repository)

The system clones the repository, loads all `.py` files, splits them into 1000-character chunks with 200-character overlap, embeds each chunk into a 384-dimensional vector using a local HuggingFace model, and persists the vectors to ChromaDB on disk.

**Query** (every question)

The user's question is embedded using the same model, the top 6 most similar code chunks are retrieved from ChromaDB via cosine similarity, and a prompt is built combining the system instruction, conversation history, retrieved code context, and the question. This is sent to Groq Llama 3.3 70B, which returns an answer with source file references.

---

## Project Structure

```
source-code-analyzer/
├── app.py                  # Flask web server — entry point
├── chat.py                 # RAG conversation engine
├── ingest.py               # Repository ingestion pipeline
├── requirements.txt        # Python dependencies
├── .env                    # API key (never commit this)
├── templates/
│   └── index.html          # Web UI
├── static/
│   ├── css/style.css
│   └── js/app.js
├── repo/                   # Auto-created: cloned repository
└── db/                     # Auto-created: ChromaDB vector store
```

---

## Installation

**Prerequisites:** Python 3.10+, Git, and a free Groq API key from [console.groq.com](https://console.groq.com).

```bash
# Clone the repository
git clone https://github.com/your-username/source-code-analyzer.git
cd source-code-analyzer

# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Add your API key
echo "GROQ_API_KEY=gsk_your-key-here" > .env

# Run the app
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

> Note: The first run downloads a ~90MB HuggingFace embedding model. This happens once and is cached locally.

---

## Usage

1. Paste a public GitHub repository URL into the top input field
2. Click **Analyze Repository** and wait 1–3 minutes for ingestion
3. Ask questions about the codebase in the chat input

**Example questions:**
```
What does this project do?
What are the main classes and functions?
How does the scheduling mechanism work?
What is the entry point of the application?
```

The system retains the last 6 question-answer pairs as context, so follow-up questions work naturally.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web interface |
| `POST` | `/chatbot` | Accepts a GitHub URL and triggers ingestion |
| `GET` | `/get?msg=...` | Accepts a question and returns an AI-generated answer |

---

## Configuration

Key parameters can be adjusted directly in the source files:

| File | Parameter | Default | Description |
|------|-----------|---------|-------------|
| `ingest.py` | `CHUNK_SIZE` | `1000` | Characters per code chunk |
| `ingest.py` | `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `chat.py` | `k` | `6` | Number of chunks retrieved per question |
| `chat.py` | `temperature` | `0.2` | Lower = more precise answers |
| `chat.py` | `max_tokens` | `2000` | Maximum response length |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `GROQ_API_KEY not found` | Ensure `.env` exists with `GROQ_API_KEY=gsk_...` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv activated |
| Clone failed | Confirm the URL begins with `https://github.com/` and the repo is public |
| No Python files found | The repository does not contain `.py` files |
| `429 Rate limit error` | Wait 60 seconds — free Groq tier allows 30 requests/minute |
| Port 5000 already in use | Change the port in `app.py`: `app.run(port=8080)` |

---

## References

- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS.
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [HuggingFace Sentence Transformers](https://huggingface.co/sentence-transformers)
