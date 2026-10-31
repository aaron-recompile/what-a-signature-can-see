#!/usr/bin/env python3
"""
build_html.py — render the book/game/blog Markdown into styled dark-theme HTML
pages (so links from the landing page open a real webpage, not raw .md).

Needs: pandoc. Run:  python3 build_html.py   (re-run whenever the .md changes)
"""
import subprocess, os, html

HERE = os.path.dirname(os.path.abspath(__file__))

EN_TITLE = "What a Signature Can See"

# (source md, output html, page title, path-to-home)
# A title of None means "use the first '# ' heading of the source file"; this
# keeps the Chinese edition's titles out of this script. English pages get an
# English-only topbar; Chinese-edition pages (source name ending in _CN.md)
# keep a bilingual "EN · CN" topbar.
DOCS = [
    ("MANUSCRIPT_EN.md", "book-en.html", "What a Signature Can See — the book", "./"),
    ("MANUSCRIPT_CN.md", "book-cn.html", None, "./"),
    ("APPENDIX_A_strip_game_CN.md", "game-cn.html", None, "./"),
    ("sighash-playground/blog/blog1_what_a_signature_signs.md",
     "sighash-playground/blog/blog1.html", "What a Bitcoin Signature Actually Signs", "../../"),
    ("sighash-playground/blog/blog2_when_two_signatures_collide.md",
     "sighash-playground/blog/blog2.html", "When Two Signatures Collide", "../../"),
]

CSS = """
:root{--bg:#0d1117;--panel:#161b22;--line:#30363d;--fg:#e6edf3;--dim:#8b949e;--accent:#58a6ff;--seen:#2ea043;--pink:#db61a2}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:17px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif}
.topbar{position:sticky;top:0;background:rgba(13,17,23,.9);backdrop-filter:blur(6px);
  border-bottom:1px solid var(--line);padding:11px 20px;font-size:14px}
.topbar a{color:var(--accent);text-decoration:none} .topbar a:hover{text-decoration:underline}
main{max-width:760px;margin:0 auto;padding:34px 22px 100px}
h1{font-size:30px;line-height:1.25;margin:8px 0 18px}
h2{font-size:22px;margin:44px 0 14px;padding-top:22px;border-top:1px solid var(--line)}
h3{font-size:18px;margin:30px 0 10px}
h1+*,h2+*{margin-top:0}
p,li{color:#c9d1d9} strong,b{color:var(--fg)}
a{color:var(--accent)} a:hover{text-decoration:underline}
blockquote{margin:18px 0;padding:6px 18px;border-left:3px solid var(--accent);
  background:#12182080;color:var(--dim);border-radius:0 6px 6px 0}
blockquote strong{color:var(--fg)}
code{font-family:"SF Mono",ui-monospace,Menlo,Consolas,monospace;font-size:.88em;
  background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:1px 5px}
pre{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:14px 16px;overflow:auto}
pre code{background:none;border:0;padding:0;font-size:13px;line-height:1.55}
table{border-collapse:collapse;margin:16px 0;font-size:14.5px;display:block;overflow:auto}
th,td{border:1px solid var(--line);padding:7px 11px;text-align:left;vertical-align:top}
th{background:var(--panel);color:var(--fg)}
hr{border:0;border-top:1px solid var(--line);margin:34px 0}
img{max-width:100%}
em{color:#c9d1d9}
ul,ol{padding-left:24px}
.foot{color:var(--dim);font-size:13px;margin-top:40px;border-top:1px solid var(--line);padding-top:16px}
"""

def first_h1(src):
    with open(os.path.join(HERE, src), encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()
    return EN_TITLE

def render(src, out, title, home):
    src_path = os.path.join(HERE, src)
    if title is None:
        title = first_h1(src)
    if src.endswith("_CN.md"):
        topbar = f"{EN_TITLE} · {first_h1('MANUSCRIPT_CN.md')}"
    else:
        topbar = EN_TITLE
    body = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html5", "--no-highlight", src_path],
        capture_output=True, text=True, check=True).stdout
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="topbar">← <a href="{home}">{html.escape(topbar, quote=False)}</a></div>
<main>
{body}
<div class="foot">Part of <a href="{home}">What a Signature Can See</a> · try the <a href="{home}sighash-playground/">interactive playground</a>.</div>
</main>
</body>
</html>
"""
    out_path = os.path.join(HERE, out)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"  {src}  ->  {out}  ({len(page)} bytes)")

if __name__ == "__main__":
    print("rendering markdown -> html:")
    for src, out, title, home in DOCS:
        render(src, out, title, home)
    print("done.")
