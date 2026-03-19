
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    print("=" * 60)
    print("ERROR: GROQ_API_KEY not found!")
    print("1. Go to https://console.groq.com")
    print("2. Sign up with Google (FREE)")
    print("3. Create API Key")
    print("4. Add to .env file: GROQ_API_KEY=gsk_your-key")
    print("=" * 60)
    exit(1)

from ingest import ingest_repository
from chat import initialize_chat, ask_question

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chatbot", methods=["POST"])
def chatbot():
    github_url = request.form.get("msg", "").strip()

    if not github_url:
        return jsonify({"response": "Please enter a GitHub repository URL."})

    if not github_url.startswith("https://github.com/"):
        return jsonify({
            "response": "Please enter a valid GitHub URL (starting with https://github.com/)"
        })

    try:
        print(f"\n{'='*60}")
        print(f"[APP] Received repository URL: {github_url}")
        print(f"{'='*60}\n")

        ingest_repository(github_url)
        initialize_chat()

        return jsonify({
            "response": "Repository ingested successfully! You can now ask questions about the codebase. Try asking: What does this project do?"
        })

    except ValueError as e:
        return jsonify({"response": str(e)})
    except Exception as e:
        print(f"[APP] Error during ingestion: {e}")
        return jsonify({
            "response": f"Error processing repository: {str(e)}. Make sure the URL is correct and the repository is public."
        })


@app.route("/get", methods=["GET"])
def get_response():
    question = request.args.get("msg", "").strip()

    if not question:
        return jsonify({"response": "Please ask a question about the code."})

    try:
        result = ask_question(question)
        answer = result["answer"]
        sources = result.get("sources", [])

        if sources:
            source_text = "\n".join([f"  {s}" for s in sources[:4]])
            answer += f"\n\nSources:\n{source_text}"

        return jsonify({"response": answer})

    except RuntimeError as e:
        return jsonify({"response": str(e)})
    except Exception as e:
        print(f"[APP] Error answering question: {e}")
        return jsonify({
            "response": f"Error: {str(e)}. Please try rephrasing your question."
        })


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Source Code Analyzer (FREE Edition)")
    print("  Using: Groq Llama 3 (free) + HuggingFace (free)")
    print("  Open browser: http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
