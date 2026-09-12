import os
import json
import tempfile

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from .ai_provider import AIProvider
from .pdf_service import extract_pdf


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
    """
    Validate and prepare chat messages for the AI provider.
    """

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

                # Send provider information once
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

                # Send streamed token
                if item.get("type") == "token":

                    yield (
                        "data: "
                        + json.dumps({
                            "type": "token",
                            "token": item.get("token", "")
                        })
                        + "\n\n"
                    )

            # Tell frontend streaming is finished
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

    # Check whether a file was uploaded
    if "file" not in request.files:

        return jsonify({
            "error": "No PDF file provided."
        }), 400

    file = request.files["file"]

    # Check filename
    if not file.filename:

        return jsonify({
            "error": "No file selected."
        }), 400

    # Only allow PDF files
    if not file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    filename = secure_filename(file.filename)

    temp_path = None

    try:

        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            file.save(temp_file.name)

            temp_path = temp_file.name

        # Extract PDF text
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

        # Delete temporary PDF
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