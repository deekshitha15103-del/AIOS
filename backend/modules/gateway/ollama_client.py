import json
import os
import urllib.request


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://api.openai.com/v1/chat/completions",
)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_answer(prompt: str) -> str:
    if LLM_PROVIDER == "openai":
        return generate_openai_answer(prompt)

    return generate_ollama_answer(prompt)


def generate_ollama_answer(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 250,
        },
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


def generate_fallback_answer(prompt: str) -> str:
    return (
        "The document was uploaded and relevant context was retrieved successfully. "
        "However, the hosted LLM provider is currently unavailable due to API quota or rate limits. "
        "Please try again later, or run AIOS locally with Ollama for full answer generation."
    )


def generate_openai_answer(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return generate_fallback_answer(prompt)

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are AIOS, an enterprise AI knowledge assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }

    req = urllib.request.Request(
        OPENAI_BASE_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))

        return result["choices"][0]["message"]["content"]

    except Exception:
        return generate_fallback_answer(prompt)


def generate_stream(prompt: str):
    answer = generate_answer(prompt)

    for token in answer.split():
        yield token + " "