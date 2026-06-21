import json
import os
import subprocess
from datetime import datetime

HISTORY_FILE = "/home/danny/.speedtest_history.json"
MAX_ENTRIES = 60  # 30 days of twice-daily results


def run():
    print("Running speedtest...")
    try:
        result = subprocess.run(
            ["/usr/bin/speedtest", "--accept-license", "--accept-gdpr", "--format=json"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"Speedtest failed (exit {result.returncode}): {result.stderr.strip()}")
            return
        data = json.loads(result.stdout)
        # Ookla reports bandwidth in bytes/sec; convert to Mbps
        download_mbps = round(data["download"]["bandwidth"] * 8 / 1_000_000, 2)
        upload_mbps = round(data["upload"]["bandwidth"] * 8 / 1_000_000, 2)
        ping_ms = round(data["ping"]["latency"], 1)
    except subprocess.TimeoutExpired:
        print("Speedtest failed: timed out after 120s")
        return
    except Exception as e:
        print(f"Speedtest failed: {e}")
        return

    entry = {
        "timestamp": datetime.now().isoformat(),
        "download": download_mbps,
        "upload": upload_mbps,
        "ping": ping_ms,
    }

    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(entry)
    history = history[-MAX_ENTRIES:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    print(f"Done: ↓{download_mbps} Mbps  ↑{upload_mbps} Mbps  ping:{ping_ms} ms")


if __name__ == "__main__":
    run()
