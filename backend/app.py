from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from .ai_provider import AIProvider
import os
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

ai = AIProvider()


def system_prompt():
    return {
        "role": "system",
        "content": (
            "You are Nexora AI, a helpful and intelligent AI assistant. "
            "Give accurate, clear and useful answers. "
            "Think carefully before answering. "
            "Use Markdown when appropriate. "
            "For programming questions, provide clean and understandable code. "
            "Never pretend to browse the web, read a file, or use a tool "
            "unless that capability has actually been provided."
        )
    }


def prepare_messages(data):
    if not data or "messages" not in data:
        raise ValueError("messages field is required")

    messages = data["messages"]

    if not isinstance(messages, list) or len(messages) == 0:
        raise ValueError("messages must be a non-empty list")

    clean_messages = []

    for message in messages:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content", "")

        if role not in ["user", "assistant"]:
            continue

        if not isinstance(content, str):
            content = str(content)

        clean_messages.append({
            "role": role,
            "content": content
        })

    if not clean_messages:
        raise ValueError("No valid messages provided")

    return [system_prompt()] + clean_messages


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "app": "Nexora AI Backend",
        "primary_provider": "Gemini",
        "fallback_provider": "Groq"
    })


@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json()
        messages = prepare_messages(data)

        result = ai.generate(messages)

        return jsonify(result)

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():

    try:
        data = request.get_json()
        messages = prepare_messages(data)

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

    def generate():

        try:

            provider_sent = False

            for item in ai.stream(messages):

                if item["type"] == "token":

                    if not provider_sent:

                        yield (
                            "data: "
                            + json.dumps({
                                "type": "provider",
                                "provider": item["provider"],
                                "model": item["model"]
                            })
                            + "\n\n"
                        )

                        provider_sent = True

                    yield (
                        "data: "
                        + json.dumps({
                            "type": "token",
                            "token": item["token"]
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
            yield (
                "data: "
                + json.dumps({
                    "type": "provider",
                    "provider": result["provider"],
                    "model": result["model"]
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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )