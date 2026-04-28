import os
import json
import time
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.expanduser("~/nexus"), ".env"))

NEXUS_ROOT = os.path.expanduser("~/nexus")
SOUL_PATH = os.path.join(NEXUS_ROOT, "soul.md")
VAULT_PATH = os.path.join(NEXUS_ROOT, "memory", "vault.json")
ERROR_LOG_PATH = os.path.join(NEXUS_ROOT, "memory", "error_logs.json")

DEFAULT_MODEL = "gemini-2.5-flash-lite"
SMART_MODEL = "gemini-2.5-pro"

MAX_RETRIES = 4
BASE_BACKOFF = 2


def _log_error(source, message):
    try:
        os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
        logs = []
        if os.path.exists(ERROR_LOG_PATH):
            with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        logs.append({
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "source": source,
            "error": message
        })
        with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass


def _load_soul():
    try:
        if os.path.exists(SOUL_PATH):
            with open(SOUL_PATH, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        _log_error("brain._load_soul", str(e))
    return "You are Nexus, a helpful AI assistant. Refer to the user as Sir."


def _load_vault_context():
    try:
        if os.path.exists(VAULT_PATH):
            with open(VAULT_PATH, "r", encoding="utf-8") as f:
                vault = json.load(f)
            context_parts = []
            user_name = vault.get("user_name", "Asa")
            context_parts.append(f"User name: {user_name}")
            prefs = vault.get("preferences", {})
            if prefs:
                context_parts.append(f"Preferences: {json.dumps(prefs)}")
            facts = vault.get("facts", [])
            if facts:
                context_parts.append("Known facts about the user:")
                for fact in facts:
                    context_parts.append(f"  - {fact}")
            assignments = vault.get("assignments", [])
            if assignments:
                context_parts.append(f"Upcoming assignments: {len(assignments)} pending")
                for a in assignments[:5]:
                    due = a.get("due_at", "unknown due date")
                    context_parts.append(f"  - {a.get('name', 'Unnamed')} due {due}")
            grades = vault.get("grades", {})
            if grades:
                context_parts.append("Current grades:")
                for course, grade in list(grades.items())[:5]:
                    context_parts.append(f"  - {course}: {grade}")
            return "\n".join(context_parts)
    except Exception as e:
        _log_error("brain._load_vault_context", str(e))
    return ""


def _build_system_prompt():
    soul = _load_soul()
    vault_ctx = _load_vault_context()
    parts = [soul]
    if vault_ctx:
        parts.append("\n\n--- CURRENT CONTEXT ---\n" + vault_ctx)
    parts.append(
        "\n\n--- FORMATTING RULES ---\n"
        "Respond in plain conversational English only. "
        "No markdown. No code blocks. No bullet points. No numbered lists. "
        "No asterisks. No hashtags. No headers. "
        "Just natural sentences as if speaking aloud. "
        "Answer directly first, then add context if needed."
    )
    return "\n".join(parts)


def think(prompt, model=None, use_web=False):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "Gemini API key not configured. Please set GEMINI_API_KEY in your .env file."

    genai.configure(api_key=api_key)

    if model is None:
        model = DEFAULT_MODEL

    if use_web:
        try:
            from core.search import web_research
            web_results = web_research(prompt, max_results=2)
            prompt = (
                f"The user asked: {prompt}\n\n"
                f"Here is relevant web research to help answer:\n\n{web_results}\n\n"
                f"Using this information, answer the user's question directly and naturally."
            )
        except Exception as e:
            _log_error("brain.think.web_search", str(e))

    system_prompt = _build_system_prompt()

    for attempt in range(MAX_RETRIES):
        try:
            gemini_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=system_prompt
            )
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            err_str = str(e)
            _log_error("brain.think", f"Attempt {attempt + 1}: {err_str}")
            if "429" in err_str or "quota" in err_str.lower() or "rate" in err_str.lower():
                wait = BASE_BACKOFF ** (attempt + 1)
                print(f"Rate limited. Waiting {wait}s before retry...")
                time.sleep(wait)
                continue
            return f"Error communicating with Gemini: {err_str}"

    return "Gemini is rate limited. Please try again in a moment."


if __name__ == "__main__":
    print("Testing brain module...")
    response = think("What time is it right now roughly?")
    print("Brain response:", response)
    print("\nBrain module OK.")
