import os
import subprocess
import time
from typing import Optional

import pandas as pd

# Path to TSV file (relative to script or absolute)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TSV_PATH = os.path.join(SCRIPT_DIR, "quizlet_export.tsv")

# Interval between notifications (in seconds)
NOTIFICATION_INTERVAL = 60

# Optional: big character as notification image (needs Pillow + terminal-notifier)


def _terminal_notifier_path() -> Optional[str]:
    """Return path to terminal-notifier binary, or None if not found."""
    import shutil
    if shutil.which("terminal-notifier"):
        return "terminal-notifier"
    for path in ("/opt/homebrew/bin/terminal-notifier", "/usr/local/bin/terminal-notifier"):
        if os.path.isfile(path):
            return path
    return None


def _make_char_image(char: str) -> Optional[str]:
    """Generate a small image with the character in large font. Returns path or None if Pillow/font missing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    # macOS CJK fonts (first available)
    for font_path in (
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ):
        if not os.path.isfile(font_path):
            continue
        try:
            font = ImageFont.truetype(font_path, 64)
            break
        except Exception:
            continue
    else:
        return None
    size = 128
    padding = 28  # margin so the character doesn't touch the edges
    inner = size - 2 * padding
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Center the character in the inner area (with padding)
    try:
        bbox = draw.textbbox((0, 0), char, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = padding + (inner - w) // 2 - bbox[0]
        y = padding + (inner - h) // 2 - bbox[1]
    except AttributeError:
        w, h = draw.textsize(char, font=font)
        x = padding + (inner - w) // 2
        y = padding + (inner - h) // 2
    draw.text((x, y), char, font=font, fill=(0, 0, 0, 255))
    path = os.path.join("/tmp", "notif_char.png")
    img.save(path)
    return path


def load_cards():
    """Load TSV: no header, columns are [character, pinyin_meaning]."""
    df = pd.read_csv(TSV_PATH, sep="\t", header=None, names=["character", "pinyin_meaning"])
    return df


def send_notification(pronounce: bool = False, verbose: bool = False):
    df = load_cards()
    if df.empty:
        print("No rows in TSV.")
        return
    row = df.sample().iloc[0]
    char = row["character"].strip()
    pinyin_meaning = str(row["pinyin_meaning"]).strip()
    title = char
    message = pinyin_meaning
    # Sanitize: no newlines (can break both notifiers)
    title_clean = title.replace("\n", " ").replace("\r", " ").strip()
    message_clean = message.replace("\n", " ").replace("\r", " ").strip()
    # Prefer terminal-notifier with character image (big character as logo) if available
    image_path = _make_char_image(char)
    tn_path = _terminal_notifier_path()
    if tn_path:
        # terminal-notifier -contentImage expects a URL (e.g. file:///path)
        content_image_arg = []
        if image_path and os.path.isfile(image_path):
            content_image_arg = ["-contentImage", "file://" + image_path]
        # Escape leading [ or ( so terminal-notifier recognizes the value (see -help)
        msg_arg = message_clean
        if msg_arg and msg_arg[0] in ("[", "("):
            msg_arg = "\\" + msg_arg
        r = subprocess.run(
            [tn_path, "-title", title_clean, "-message", msg_arg] + content_image_arg,
            capture_output=True,
            text=True,
        )
        sent = r.returncode == 0
        if verbose:
            if sent:
                print("Notification sent via terminal-notifier.")
            else:
                print("terminal-notifier failed:", r.stderr or r.stdout or f"exit {r.returncode}")
    else:
        sent = False
        if verbose:
            print("terminal-notifier not found, using osascript.")
    if not sent:
        # Fallback: osascript (no image; escape only \ and " for AppleScript)
        message_esc = message_clean.replace("\\", "\\\\").replace('"', '\\"')
        title_esc = title_clean.replace("\\", "\\\\").replace('"', '\\"')
        script = f'display notification "{message_esc}" with title "{title_esc}"'
        r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if verbose and r.returncode != 0:
            print("osascript failed:", r.stderr or r.stdout or f"exit {r.returncode}")
    if pronounce:
        # Speak the character with Tingting voice (Mandarin)
        subprocess.run(["say", "-v", "Tingting", char], check=False)


def run_regularly(pronounce: bool = False, verbose: bool = False):
    """Send a notification every NOTIFICATION_INTERVAL seconds."""
    print(f"Notifications every {NOTIFICATION_INTERVAL}s. Stop with Ctrl+C.")
    if pronounce:
        print("Pronunciation enabled (say -v Tingting).")
    while True:
        send_notification(pronounce=pronounce, verbose=verbose)
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
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--pronounce", "-p", "--verbose", "-v")]
    if args and args[0] == "--once":
        send_notification(pronounce=pronounce, verbose=verbose)
    else:
        run_regularly(pronounce=pronounce, verbose=verbose)
