import os
import json
import tempfile

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from ai_provider import AIProvider
from pdf_service import extract_pdf, retrieve_relevant_pages


# Load environment variables
load_dotenv()


# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)


# Initialize AI provider
ai = AIProvider()


def system_prompt():
    return """
You are Nexora AI, a helpful and intelligent AI assistant.

Give accurate, clear and useful answers.
Think carefully before answering.
Use Markdown when appropriate.

For programming questions, provide clean and understandable code.

Never pretend to browse the web, read a file, or use a tool
unless that capability has actually been provided.
"""


def prepare_messages(messages):

    if not isinstance(messages, list):
        raise ValueError("messages must be a list.")

    clean_messages = []

    for message in messages:

        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")

        if role not in ["user", "assistant"]:
            continue

        if not isinstance(content, str):
            continue

        content = content.strip()

        if not content:
            continue

        clean_messages.append({
            "role": role,
            "content": content
        })

    if not clean_messages:
        raise ValueError("No valid messages provided.")

    return [
        {
            "role": "system",
            "content": system_prompt()
        }
    ] + clean_messages


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "app": "Nexora AI Backend",
        "status": "OK",
        "primary_provider": "Gemini",
        "fallback_provider": "Groq"
    })


# ============================================================
# NORMAL CHAT
# ============================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        messages = data.get("messages", [])

        messages = prepare_messages(messages)

        result = ai.generate(messages)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# STREAMING CHAT
# ============================================================

@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():

    try:

        data = request.get_json(silent=True) or {}

        messages = data.get("messages", [])

        messages = prepare_messages(messages)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400

    def generate():

        provider_sent = False

        try:

            for item in ai.stream(messages):

                if not provider_sent:

                    yield (
                        "data: "
                        + json.dumps({
                            "type": "provider",
                            "provider": item.get("provider"),
                            "model": item.get("model")
                        })
                        + "\n\n"
                    )

                    provider_sent = True

                if item.get("type") == "token":

                    yield (
                        "data: "
                        + json.dumps({
                            "type": "token",
                            "token": item.get("token", "")
                        })
                        + "\n\n"
                    )

            yield (
                "data: "
                + json.dumps({
                    "type": "done"
                })
                + "\n\n"
            )

        except Exception as e:

            yield (
                "data: "
                + json.dumps({
                    "type": "error",
                    "error": str(e)
                })
                + "\n\n"
            )

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

@app.route("/api/pdf/extract", methods=["POST"])
def extract_pdf_endpoint():

    if "file" not in request.files:

        return jsonify({
            "error": "No PDF file provided."
        }), 400

    file = request.files["file"]

    if not file.filename:

        return jsonify({
            "error": "No file selected."
        }), 400

    if not file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    filename = secure_filename(file.filename)

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            file.save(temp_file.name)

            temp_path = temp_file.name

        result = extract_pdf(temp_path)

        return jsonify({
            "filename": filename,
            "page_count": result["page_count"],
            "pages": result["pages"],
            "text_length": len(result["text"])
        })

    except Exception as e:

        return jsonify({
            "error": f"PDF extraction failed: {str(e)}"
        }), 500

    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================================
# PDF QUESTION & ANSWER
# ============================================================

@app.route("/api/pdf/ask", methods=["POST"])
def ask_pdf():

    if "file" not in request.files:

        return jsonify({
            "error": "No PDF file provided."
        }), 400

    file = request.files["file"]

    if not file.filename:

        return jsonify({
            "error": "No file selected."
        }), 400

    if not file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    question = request.form.get("question", "").strip()

    if not question:

        return jsonify({
            "error": "No question provided."
        }), 400

    filename = secure_filename(file.filename)

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save uploaded PDF temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            file.save(temp_file.name)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Extract PDF
        # ----------------------------------------------------

        pdf_result = extract_pdf(temp_path)

        # ----------------------------------------------------
        # Retrieve relevant pages
        # ----------------------------------------------------

        relevant_pages = retrieve_relevant_pages(
            pdf_result["pages"],
            question,
            top_k=5
        )

        if not relevant_pages:

            return jsonify({
                "error": "No readable text was found in this PDF."
            }), 400

        # ----------------------------------------------------
        # Build context for Gemini/Groq
        # ----------------------------------------------------

        context_parts = []

        source_pages = []

        for page in relevant_pages:

            page_number = page["page"]
            page_text = page["text"]

            source_pages.append(page_number)

            context_parts.append(
                f"--- PAGE {page_number} ---\n"
                f"{page_text}"
            )

        context = "\n\n".join(context_parts)

        # ----------------------------------------------------
        # Ask AI using retrieved PDF context
        # ----------------------------------------------------

        pdf_system_prompt = """
You are Nexora AI's PDF analysis assistant.

Answer the user's question using the provided PDF context.

IMPORTANT RULES:

1. Use only the information contained in the provided PDF context.
2. Do not invent information that is not present.
3. If the answer cannot be found in the provided context, clearly say that
   the information could not be found in the relevant PDF content.
4. When possible, mention the PDF page number where the information was found.
5. Give a clear and concise answer.
6. Use Markdown when useful.
"""

        user_prompt = f"""
PDF FILE:
{filename}

USER QUESTION:
{question}

RELEVANT PDF CONTENT:

{context}

Answer the user's question based only on the relevant PDF content.
"""

        messages = [
            {
                "role": "system",
                "content": pdf_system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        result = ai.generate(messages)

        return jsonify({
            "filename": filename,
            "question": question,
            "answer": result["reply"],
            "provider": result.get("provider"),
            "model": result.get("model"),
            "source_pages": source_pages
        })

    except Exception as e:

        return jsonify({
            "error": f"PDF question answering failed: {str(e)}"
        }), 500

    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )