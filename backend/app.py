from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")

MAX_ATTACHMENT_CHARS = 20000


def system_prompt():
    return {
        "role": "system",
        "content": (
            "You are Qualibytes GPT, a helpful and friendly AI assistant. "
            "Give clear, useful and concise answers. "
            "Use Markdown when appropriate. "
            "For programming questions, provide clean and understandable code. "
            "Do not claim to browse the internet or use tools unless tools are actually provided."
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

    attachments = data.get("attachments", [])

    if isinstance(attachments, list) and attachments:
        attachment_text = []

        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue

            name = attachment.get("name", "attachment")
            content = attachment.get("content", "")

            if content:
                content = str(content)[:MAX_ATTACHMENT_CHARS]

                attachment_text.append(
                    f"\n\n[Attached file: {name}]\n"
                    f"{content}\n"
                    f"[End attached file]"
                )

        if attachment_text and clean_messages:
            clean_messages[-1]["content"] += "".join(attachment_text)

    return [system_prompt()] + clean_messages


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK",
        "app": "Qualibytes GPT Backend",
        "model": MODEL_NAME
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        full_messages = prepare_messages(data)

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": full_messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()
        reply = result["message"]["content"].strip()

        return jsonify({"reply": reply})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Ollama service is not reachable."
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Ollama timed out. The model may still be loading."
        }), 504

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():

    try:
        data = request.get_json()
        full_messages = prepare_messages(data)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    def generate():
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": MODEL_NAME,
                    "messages": full_messages,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500
                    }
                },
                stream=True,
                timeout=(10, 3600)
            )

            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):

                if not line:
                    continue

                try:
                    chunk = json.loads(line)

                    if "message" in chunk:
                        token = chunk["message"].get("content", "")

                        if token:
                            yield (
                                "data: "
                                + json.dumps({
                                    "type": "token",
                                    "token": token
                                })
                                + "\n\n"
                            )

                    if chunk.get("done"):
                        yield (
                            "data: "
                            + json.dumps({
                                "type": "done"
                            })
                            + "\n\n"
                        )
                        break

                except json.JSONDecodeError:
                    continue

        except requests.exceptions.ConnectionError:
            yield (
                "data: "
                + json.dumps({
                    "type": "error",
                    "error": "Ollama service is not reachable."
                })
                + "\n\n"
            )

        except requests.exceptions.Timeout:
            yield (
                "data: "
                + json.dumps({
                    "type": "error",
                    "error": "Ollama timed out."
                })
                + "\n\n"
            )

        except requests.exceptions.RequestException as e:
            yield (
                "data: "
                + json.dumps({
                    "type": "error",
                    "error": str(e)
                })
                + "\n\n"
            )

        except GeneratorExit:
            return

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