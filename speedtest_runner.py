import json
import os
import speedtest
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".speedtest_history.json")
MAX_ENTRIES = 60  # 30 days of twice-daily results


def run():
    print("Running speedtest...")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_mbps = round(st.download() / 1_000_000, 2)
        upload_mbps = round(st.upload() / 1_000_000, 2)
        ping_ms = round(st.results.ping, 1)
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
