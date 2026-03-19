
import os
import shutil
from git import Repo
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

REPO_DIR = os.path.join(os.path.dirname(__file__), "repo")
DB_DIR = os.path.join(os.path.dirname(__file__), "db")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def clone_repository(github_url):
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)
        print(f"[INGEST] Cleaned up old repository at {REPO_DIR}")
    print(f"[INGEST] Cloning repository: {github_url}")
    Repo.clone_from(github_url, REPO_DIR)
    print(f"[INGEST] Repository cloned successfully to {REPO_DIR}")
    return REPO_DIR


def load_python_files(repo_path):
    print(f"[INGEST] Loading Python files from {repo_path}")
    loader = DirectoryLoader(
        repo_path,
        glob="**/*.py",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()
    print(f"[INGEST] Loaded {len(documents)} Python files")
    return documents


def split_documents(documents):
    print(f"[INGEST] Splitting {len(documents)} documents into chunks")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"[INGEST] Created {len(chunks)} chunks")
    return chunks


def get_embeddings():
    print(f"[INGEST] Loading embedding model: {EMBEDDING_MODEL}")
    print("[INGEST] (First time will download ~90MB model - only once!)")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    print("[INGEST] Embedding model loaded successfully")
    return embeddings


def create_vector_store(chunks):
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)
        print(f"[INGEST] Cleaned up old vector store at {DB_DIR}")
    os.makedirs(DB_DIR, exist_ok=True)
    print("[INGEST] Creating embeddings and vector store...")
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print(f"[INGEST] Vector store created with {len(chunks)} vectors")
    return vector_store


def ingest_repository(github_url):
    print("=" * 60)
    print("[INGEST] Starting ingestion pipeline")
    print(f"[INGEST] Repository: {github_url}")
    print("=" * 60)
    repo_path = clone_repository(github_url)
    documents = load_python_files(repo_path)
    if not documents:
        raise ValueError(
            "No Python files found in this repository. "
            "Make sure the repository contains .py files."
        )
    chunks = split_documents(documents)
    vector_store = create_vector_store(chunks)
    print("=" * 60)
    print("[INGEST] Ingestion pipeline complete!")
    print("=" * 60)
    return vector_store
