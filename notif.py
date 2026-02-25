import pandas as pd
import os
import time

# Path to TSV file (relative to script or absolute)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TSV_PATH = os.path.join(SCRIPT_DIR, "quizlet_export.tsv")

# Interval between notifications (in seconds)
NOTIFICATION_INTERVAL = 440


def load_cards():
    """Load TSV: no header, columns are [character, pinyin_meaning]."""
    df = pd.read_csv(TSV_PATH, sep="\t", header=None, names=["character", "pinyin_meaning"])
    return df


def send_notification():
    df = load_cards()
    if df.empty:
        print("No rows in TSV.")
        return
    row = df.sample().iloc[0]
    char = row["character"].strip()
    # pinyin_meaning is e.g. "bèi - coquillage (部 est)"
    pinyin_meaning = str(row["pinyin_meaning"]).strip()
    title = f"Chinois : {char}"
    message = pinyin_meaning
    # Escape quotes for AppleScript
    message_esc = message.replace("\\", "\\\\").replace('"', '\\"')
    title_esc = title.replace("\\", "\\\\").replace('"', '\\"')
    os.system(
        f'osascript -e \'display notification "{message_esc}" with title "{title_esc}"\''
    )


def run_regularly():
    """Send a notification every NOTIFICATION_INTERVAL seconds."""
    print(f"Notifications every {NOTIFICATION_INTERVAL}s. Stop with Ctrl+C.")
    while True:
        send_notification()
        time.sleep(NOTIFICATION_INTERVAL)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        send_notification()
    else:
        run_regularly()
