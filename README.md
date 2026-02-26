# regular_vocab_notif

Simple macOS notifier that displays random vocabulary cards from a TSV export (e.g. Quizlet). Notifications show the character with pinyin and translation below; optional pronunciation with the Tingting voice.

## Requirements

- macOS (uses `osascript` for system notifications and `say` for pronunciation)
- Python 3
- pandas (`pip install pandas`)

## Data format

The script reads `quizlet_export.tsv` in the same folder. It expects **two tab-separated columns** without a header:

1. The character (one or more)
2. Pinyin and meaning (free text, e.g. `bèi - coquillage (部 est)`)

Example:

```
贝	bèi - coquillage (部 est)
文	wén - écriture, texte
分钟	fēnzhōng - minute
```

## Notification display

- **Title:** the character only (e.g. `贝`)
- **Message (below):** pinyin and translation (e.g. `bèi - coquillage (部 est)`)

## Usage

Run the script with Python from the project directory:

```bash
# Run in a loop (notification every NOTIFICATION_INTERVAL seconds)
python notif.py

# Single notification
python notif.py --once

# With pronunciation (say -v Tingting)
python notif.py --pronounce
python notif.py -p --once

# Stop all running instances (e.g. background loops)
python notif.py --clean
```

To run in the background: `nohup python notif.py &` (stop with `python notif.py --clean` or kill the process).

## Configuration

- **`NOTIFICATION_INTERVAL`** in `notif.py` — Delay in seconds between notifications (default: 440).
- **`quizlet_export.tsv`** — Replace with your own TSV export to change the cards.
- **Pronunciation** — Use `--pronounce` or `-p` when launching to hear the character with the macOS voice “Tingting” (Mandarin).
