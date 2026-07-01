import os
import sys

def get_client_and_model():
    """
    Returns (client, model_name, backend).
    client exposes .chat.completions.create(...) with the same signature regardless of backend.
    """
    backend = os.environ.get(
        "LLM_BACKEND",
        "openai" if os.environ.get("OPENAI_API_KEY") else ("groq" if os.environ.get("GROQ_API_KEY") else "ollama")
    ).lower()

    if backend == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return client, model, "openai"

    if backend == "groq":
        from groq import Groq
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        model = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        return client, model, "groq"

    # -- Ollama, via its OpenAI-compatible endpoint --------------------------
    from openai import OpenAI
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    client = OpenAI(base_url=base_url, api_key="ollama")
    model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
    return client, model, "ollama"


def check_connection(client, model, backend):
    """
    Friendly pre-flight check.
    Fail with a clear, backend-specific message instead of a raw connection traceback.
    """
    try:
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say OK in one word"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        if backend == "ollama":
            print(f"\nCould not reach Ollama at the configured base_url.", file=sys.stderr)
            print(f" 1) Is it running? -> ollama serve", file=sys.stderr)
            print(f" 2) Is the model pulled? -> ollama pull {model}", file=sys.stderr)
        elif backend == "openai":
            print(f"\nCould not reach OpenAI.", file=sys.stderr)
            print(f" Check that OPENAI_API_KEY is set correctly.", file=sys.stderr)
            print(f" Underlying error: {e}\n", file=sys.stderr)
        else:
            print(f"\nCould not reach Groq.", file=sys.stderr)
            print(f" Check that GROQ_API_KEY is set correctly.", file=sys.stderr)
            print(f" Underlying error: {e}\n", file=sys.stderr)
        return False
