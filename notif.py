import pandas as pd
import os
import subprocess
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


def send_notification(pronounce: bool = False):
    df = load_cards()
    if df.empty:
        print("No rows in TSV.")
        return
    row = df.sample().iloc[0]
    char = row["character"].strip()
    # pinyin_meaning is e.g. "bèi - coquillage (部 est)"
    pinyin_meaning = str(row["pinyin_meaning"]).strip()
    # Title = character only; message = pinyin and translation below
    title = char
    message = pinyin_meaning
    # Escape quotes for AppleScript
    message_esc = message.replace("\\", "\\\\").replace('"', '\\"')
    title_esc = title.replace("\\", "\\\\").replace('"', '\\"')
    os.system(
        f'osascript -e \'display notification "{message_esc}" with title "{title_esc}"\''
    )
    if pronounce:
        # Speak the character with Tingting voice (Mandarin)
        subprocess.run(["say", "-v", "Tingting", char], check=False)


def run_regularly(pronounce: bool = False):
    """Send a notification every NOTIFICATION_INTERVAL seconds."""
    print(f"Notifications every {NOTIFICATION_INTERVAL}s. Stop with Ctrl+C.")
    if pronounce:
        print("Pronunciation enabled (say -v Tingting).")
    while True:
        send_notification(pronounce=pronounce)
        time.sleep(NOTIFICATION_INTERVAL)


def clean():
    """Kill all running instances of this script (other than the current process)."""
    current_pid = os.getpid()
    result = subprocess.run(
        ["pgrep", "-f", "notif\\.py"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("No running instances.")
        return
    pids = [int(pid) for pid in result.stdout.strip().split() if pid and int(pid) != current_pid]
    if not pids:
        print("No other running instances.")
        return
    for pid in pids:
        try:
            os.kill(pid, 9)
        except (ProcessLookupError, PermissionError):
            pass
    print(f"Stopped {len(pids)} instance(s).")


if __name__ == "__main__":
    import sys
    if "--clean" in sys.argv:
        clean()
        sys.exit(0)
    pronounce = "--pronounce" in sys.argv or "-p" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--pronounce", "-p")]
    if args and args[0] == "--once":
        send_notification(pronounce=pronounce)
    else:
        run_regularly(pronounce=pronounce)
