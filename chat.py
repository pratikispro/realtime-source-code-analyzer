
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

DB_DIR = os.path.join(os.path.dirname(__file__), "db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_chat_history = []
_vector_store = None
_llm = None


def get_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    return embeddings


def load_vector_store():
    if not os.path.exists(DB_DIR) or not os.listdir(DB_DIR):
        raise FileNotFoundError(
            "No vector store found. Please ingest a repository first."
        )
    print("[CHAT] Loading vector store from disk...")
    embeddings = get_embeddings()
    vector_store = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings
    )
    print("[CHAT] Vector store loaded successfully")
    return vector_store


def initialize_chat():
    global _vector_store, _llm, _chat_history
    _vector_store = load_vector_store()
    _llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=2000
    )
    _chat_history = []
    print("[CHAT] Chat system initialized and ready")


def ask_question(question):
    global _vector_store, _llm, _chat_history

    if _vector_store is None or _llm is None:
        try:
            initialize_chat()
        except FileNotFoundError:
            raise RuntimeError(
                "No repository has been ingested yet. "
                "Please provide a GitHub URL first."
            )

    print(f"\n[CHAT] Question: {question}")

    relevant_docs = _vector_store.similarity_search(question, k=6)

    context_parts = []
    sources = []

    for doc in relevant_docs:
        context_parts.append(doc.page_content)
        source_path = doc.metadata.get("source", "Unknown")
        if "repo/" in source_path or "repo\\" in source_path:
            source_path = source_path.replace("\\", "/")
            source_path = source_path.split("repo/")[-1]
        if source_path not in sources:
            sources.append(source_path)

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = (
        "You are a helpful code analysis assistant. "
        "Answer questions about the codebase based on the provided code context. "
        "If the answer is not in the context, say so honestly. "
        "Be specific and reference file names and function names when possible. "
        "Format your answers clearly with bullet points or numbered lists when appropriate."
    )

    messages = [SystemMessage(content=system_prompt)]

    for past_q, past_a in _chat_history[-6:]:
        messages.append(HumanMessage(content=past_q))
        messages.append(AIMessage(content=past_a))

    user_message = f"""Based on the following code from the repository:

{context}

Question: {question}"""

    messages.append(HumanMessage(content=user_message))

    print("[CHAT] Sending to Groq Llama 3...")
    response = _llm.invoke(messages)
    answer = response.content

    _chat_history.append((question, answer))

    print(f"[CHAT] Answer generated ({len(answer)} chars)")
    print(f"[CHAT] Sources: {sources}")

    return {
        "answer": answer,
        "sources": sources
    }
