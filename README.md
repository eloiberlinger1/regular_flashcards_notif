# regular_vocab_notif

Simple macOS notifier that displays random vocabulary cards from a TSV export.

## Requirements

- macOS (uses `osascript` for system notifications)
- Python 3
- pandas (`pip install pandas`)

## Data format

The script reads `quizlet_export.tsv` in the same folder. It expects **two
tab-separated columns** without a header:

1. The character
2. Pinyin and meaning (free text)

## Usage

```bash
# Send a notification every 440 seconds (default)
python notif.py

# Send a single notification
python notif.py --once
```

## Configuration

- Edit `NOTIFICATION_INTERVAL` in `notif.py` to change the delay.
- Replace `quizlet_export.tsv` with your own export to change the cards.
