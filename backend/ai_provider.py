import os
from google import genai
from groq import Groq


class AIProvider:

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")

        self.gemini = (
            genai.Client(api_key=self.gemini_key)
            if self.gemini_key
            else None
        )

        self.groq = (
            Groq(api_key=self.groq_key)
            if self.groq_key
            else None
        )

    def generate(self, messages):
        errors = []

        if self.gemini:
            try:
                return self._gemini(messages)
            except Exception as e:
                errors.append(f"Gemini: {e}")

        if self.groq:
            try:
                return self._groq(messages)
            except Exception as e:
                errors.append(f"Groq: {e}")

        raise RuntimeError(
            "All AI providers failed. " + " | ".join(errors)
        )

    def stream(self, messages):
        """
        Yields dictionaries containing incremental response data.

        Gemini is tried first. If Gemini cannot start the stream,
        Groq is used as the fallback provider.
        """

        if self.gemini:
            try:
                for item in self._gemini_stream(messages):
                    yield item
                return
            except Exception as gemini_error:

                if self.groq:
                    try:
                        for item in self._groq_stream(messages):
                            yield item
                        return
                    except Exception as groq_error:
                        raise RuntimeError(
                            f"Gemini failed: {gemini_error} | "
                            f"Groq failed: {groq_error}"
                        )

                raise RuntimeError(
                    f"Gemini failed: {gemini_error}"
                )

        if self.groq:
            for item in self._groq_stream(messages):
                yield item
            return

        raise RuntimeError("No AI provider is configured.")

    def _build_gemini_prompt(self, messages):

        system_instruction = ""
        conversation = []

        for message in messages:

            role = message.get("role")
            content = message.get("content", "")

            if role == "system":
                system_instruction += content + "\n"

            elif role in ["user", "assistant"]:

                speaker = (
                    "User"
                    if role == "user"
                    else "Assistant"
                )

                conversation.append(
                    f"{speaker}: {content}"
                )

        return system_instruction, "\n\n".join(conversation)

    def _gemini(self, messages):

        system_instruction, prompt = (
            self._build_gemini_prompt(messages)
        )

        response = self.gemini.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.4,
                "max_output_tokens": 1500,
            },
        )

        return {
            "reply": response.text,
            "provider": "gemini",
            "model": "gemini-3.8-flash",
        }

    def _gemini_stream(self, messages):

        system_instruction, prompt = (
            self._build_gemini_prompt(messages)
        )

        stream = self.gemini.models.generate_content_stream(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.4,
                "max_output_tokens": 1500,
            },
        )

        for chunk in stream:

            text = getattr(chunk, "text", None)

            if text:
                yield {
                    "type": "token",
                    "token": text,
                    "provider": "gemini",
                    "model": "gemini-3.8-flash",
                }

    def _groq(self, messages):

        response = self.groq.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.4,
            max_completion_tokens=1500,
            stream=False,
        )

        return {
            "reply": response.choices[0].message.content,
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
        }

    def _groq_stream(self, messages):

        stream = self.groq.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.4,
            max_completion_tokens=1500,
            stream=True,
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            text = getattr(delta, "content", None)

            if text:
                yield {
                    "type": "token",
                    "token": text,
                    "provider": "groq",
                    "model": "openai/gpt-oss-20b",
                }