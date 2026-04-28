import os
import json
import datetime
import subprocess
import platform

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

NEXUS_ROOT = os.path.expanduser("~/nexus")
ERROR_LOG_PATH = os.path.join(NEXUS_ROOT, "memory", "error_logs.json")

DISTRACTION_APPS = {
    "minecraft", "steam", "discord", "netflix", "youtube",
    "reddit", "tiktok", "twitch", "roblox", "valorant",
    "fortnite"
}


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


def _get_active_app():
    if platform.system() != "Darwin":
        return None
    try:
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        _log_error("monitor._get_active_app", str(e))
        return None


def snapshot():
    stats = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "cpu_percent": None,
        "battery_percent": None,
        "battery_plugged": None,
        "disk_free_gb": None,
        "active_app": None,
        "platform": platform.system()
    }

    if PSUTIL_AVAILABLE:
        try:
            stats["cpu_percent"] = psutil.cpu_percent(interval=1)
        except Exception as e:
            _log_error("monitor.snapshot.cpu", str(e))

        try:
            battery = psutil.sensors_battery()
            if battery:
                stats["battery_percent"] = round(battery.percent, 1)
                stats["battery_plugged"] = battery.power_plugged
        except Exception as e:
            _log_error("monitor.snapshot.battery", str(e))

        try:
            disk = psutil.disk_usage("/")
            stats["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)
        except Exception as e:
            _log_error("monitor.snapshot.disk", str(e))
    else:
        _log_error("monitor.snapshot", "psutil not available")

    stats["active_app"] = _get_active_app()
    return stats


def is_slacking(app_name):
    if not app_name:
        return False
    try:
        return app_name.lower() in DISTRACTION_APPS
    except Exception as e:
        _log_error("monitor.is_slacking", str(e))
        return False


def send_notification(title, message):
    if platform.system() != "Darwin":
        print(f"[Notification] {title}: {message}")
        return
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5
        )
    except Exception as e:
        _log_error("monitor.send_notification", str(e))
        print(f"[Notification fallback] {title}: {message}")


if __name__ == "__main__":
    print("Testing monitor module...")
    stats = snapshot()
    print("System snapshot:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    app = stats.get("active_app")
    print(f"\nActive app: {app}")
    print(f"Is slacking: {is_slacking(app)}")
    send_notification("Nexus Test", "Monitor module is working correctly.")
    print("\nMonitor module OK.")
