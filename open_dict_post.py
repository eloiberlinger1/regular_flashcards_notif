#!/usr/bin/env python3
"""
On notification click: read the character from a temp file, open the browser
with a page that POSTs to the dictionary (same payload as the user's curl).
"""
import html
import os
import sys
import tempfile
import webbrowser

# Same as user's curl: POST to dictionary; we use the main dictionary URL
# so the server can respond with the dictionary page (some sites accept POST on the same path).
DICT_POST_URL = "https://www.chineseclass101.com/chinese-dictionary/"


def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    char_path = sys.argv[1]
    if not os.path.isfile(char_path):
        sys.exit(1)
    with open(char_path, "r", encoding="utf-8") as f:
        char = f.read().strip()
    try:
        os.unlink(char_path)
    except OSError:
        pass
    if not char:
        webbrowser.open(DICT_POST_URL)
        return
    # Build HTML that auto-submits a POST form (same payload: post=dictionary_reference&search_query=<char>).
    # Browser will URL-encode search_query when submitting.
    search_escaped = html.escape(char, quote=True)
    body = f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<form id="f" method="post" action="{html.escape(DICT_POST_URL, quote=True)}">
<input type="hidden" name="post" value="dictionary_reference">
<input type="hidden" name="search_query" value="{search_escaped}">
</form><script>document.getElementById("f").submit();</script>
<p>Redirecting...</p></body></html>"""
    fd, path = tempfile.mkstemp(suffix=".html", prefix="notif_dict_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(body)
    webbrowser.open("file://" + path)
    # Do not delete the file here: the browser may still be loading it.


if __name__ == "__main__":
    main()
