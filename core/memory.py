import os
import json
import datetime

NEXUS_ROOT = os.path.expanduser("~/nexus")
VAULT_PATH = os.path.join(NEXUS_ROOT, "memory", "vault.json")
ERROR_LOG_PATH = os.path.join(NEXUS_ROOT, "memory", "error_logs.json")

DEFAULT_VAULT = {
    "user_name": "Asa",
    "preferences": {"tone": "Witty", "role": "College Student"},
    "facts": [],
    "skills_registry": []
}


def _ensure_dirs():
    os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)


def load_vault():
    _ensure_dirs()
    try:
        if not os.path.exists(VAULT_PATH):
            save_vault(DEFAULT_VAULT)
            return dict(DEFAULT_VAULT)
        with open(VAULT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in DEFAULT_VAULT.items():
            if key not in data:
                data[key] = val
        return data
    except Exception as e:
        _log_error("memory.load_vault", str(e))
        return dict(DEFAULT_VAULT)


def save_vault(data):
    _ensure_dirs()
    try:
        with open(VAULT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        _log_error("memory.save_vault", str(e))


def update_memory(key, value):
    try:
        vault = load_vault()
        vault[key] = value
        save_vault(vault)
    except Exception as e:
        _log_error("memory.update_memory", str(e))


def add_fact(fact):
    try:
        vault = load_vault()
        facts = vault.get("facts", [])
        if fact not in facts:
            facts.append(fact)
            vault["facts"] = facts
            save_vault(vault)
            return True
        return False
    except Exception as e:
        _log_error("memory.add_fact", str(e))
        return False


def get_memory(key):
    try:
        vault = load_vault()
        return vault.get(key)
    except Exception as e:
        _log_error("memory.get_memory", str(e))
        return None


def _log_error(source, message):
    try:
        _ensure_dirs()
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


if __name__ == "__main__":
    print("Testing memory module...")
    vault = load_vault()
    print("Loaded vault:", json.dumps(vault, indent=2))
    update_memory("test_key", "hello_world")
    print("Updated test_key to hello_world")
    val = get_memory("test_key")
    print("Got test_key:", val)
    added = add_fact("Asa likes dark mode")
    print("Added fact:", added)
    vault = load_vault()
    print("Facts:", vault.get("facts"))
    update_memory("test_key", None)
    print("Memory module OK.")
