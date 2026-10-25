#!/usr/bin/env python3
"""
Renders source/*.md into the static pages GitHub Pages serves.

The markdown in source/ is the only copy of this text: the App Store listing and
the app itself both link here, so what is published is always what the documents
say. Run this after editing either file and commit the HTML it writes.

Deliberately stdlib-only. A legal page that cannot be rebuilt because a virtualenv
went missing is a legal page that silently drifts from its source, and the markdown
these documents use is a small enough subset to render honestly in one file.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = [
    ("privacy", "Privacy Policy", "What the app stores, and why none of it reaches us."),
    ("terms", "Terms of Service", "The terms you accept by using the app."),
]

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — sanā</title>
<meta name="description" content="{description}">
<style>
*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
:root {{
  --bg:#ffffff; --text:#111111; --body:#2e2e2e; --muted:#6b6b6b;
  --rule:#e2e2e2; --surface:#f6f6f4;
}}
@media (prefers-color-scheme:dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#0e0e0e; --text:#f2f1ee; --body:#cfcdc8; --muted:#8e8c87;
    --rule:#2a2a2a; --surface:#181817;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#0e0e0e; --text:#f2f1ee; --body:#cfcdc8; --muted:#8e8c87;
  --rule:#2a2a2a; --surface:#181817;
}}
html {{ -webkit-text-size-adjust:100%; }}
body {{
  background:var(--bg); color:var(--body);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  line-height:1.7; -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:680px; margin:0 auto; padding:0 16px; }}
header {{ border-bottom:1px solid var(--rule); }}
header .wrap {{ padding:22px 16px; display:flex; align-items:baseline; gap:14px; }}
.mark {{ font-size:1.2rem; font-weight:700; letter-spacing:.06em; color:var(--text); text-decoration:none; }}
.kicker {{ font-size:.8rem; color:var(--muted); }}
main .wrap {{ padding:44px 16px 72px; }}
h1 {{ font-size:1.9rem; line-height:1.2; font-weight:700; color:var(--text); letter-spacing:-.02em; margin-bottom:10px; }}
h2 {{ font-size:1.18rem; font-weight:700; color:var(--text); letter-spacing:-.01em; margin:40px 0 14px; }}
h3 {{ font-size:1rem; font-weight:600; color:var(--text); margin:26px 0 10px; }}
p {{ margin-bottom:15px; }}
ul,ol {{ padding-left:22px; margin-bottom:15px; }}
li {{ margin-bottom:7px; }}
strong {{ color:var(--text); font-weight:650; }}
hr {{ border:0; border-top:1px solid var(--rule); margin:34px 0; }}
a {{ color:var(--text); text-decoration:underline; text-underline-offset:2px; }}
blockquote {{
  margin:0 0 18px; padding:14px 18px; background:var(--surface);
  border-left:3px solid var(--rule); border-radius:2px;
}}
blockquote p:last-child {{ margin-bottom:0; }}
.table-wrap {{ overflow-x:auto; margin:16px 0 24px; }}
table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
th {{ text-align:left; font-weight:600; color:var(--muted); padding:10px 12px;
      background:var(--surface); border-bottom:1px solid var(--rule); }}
td {{ padding:10px 12px; border-bottom:1px solid var(--rule); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.cards {{ list-style:none; padding:0; }}
.cards li {{ border:1px solid var(--rule); border-radius:4px; padding:18px 20px; margin-bottom:12px; }}
.cards a {{ font-weight:650; font-size:1.02rem; }}
.cards span {{ display:block; color:var(--muted); font-size:.9rem; margin-top:4px; }}
footer {{ border-top:1px solid var(--rule); }}
footer .wrap {{ padding:26px 16px 40px; color:var(--muted); font-size:.85rem;
                display:flex; gap:18px; flex-wrap:wrap; }}
footer a {{ color:var(--muted); }}
</style>
</head>
<body>
<header><div class="wrap">
  <a class="mark" href="{home}">sanā</a>
  <span class="kicker">training and rehabilitation planner</span>
</div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
  <a href="{home}privacy/">Privacy Policy</a>
  <a href="{home}terms/">Terms of Service</a>
  <a href="mailto:hello@entelana.com">hello@entelana.com</a>
</div></footer>
</body>
</html>
"""

_BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")
_NUMBER = re.compile(r"^\s*\d+\.\s+(.*)$")


def inline(text: str) -> str:
    """Escape first, then re-introduce the few spans the documents use, so a
    stray `<` in the prose can never become a tag."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
                 out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


def render(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0

    def row(line: str) -> list[str]:
        return [c.strip() for c in line.strip().strip("|").split("|")]

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            out.append("<hr>")
            i += 1
            continue

        if m := re.match(r"^(#{1,6})\s+(.*)$", stripped):
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # A table: a header row, a divider of dashes, then body rows.
        if (stripped.startswith("|") and i + 1 < len(lines)
                and re.fullmatch(r"\|[\s:|-]+\|", lines[i + 1].strip())):
            head = row(stripped)
            i += 2
            body = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                body.append(row(lines[i]))
                i += 1
            cells = "".join(f"<th>{inline(c)}</th>" for c in head)
            rows = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{cells}</tr>'
                       f"</thead><tbody>{rows}</tbody></table></div>")
            continue

        if stripped.startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quoted.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + render("\n".join(quoted)) + "</blockquote>")
            continue

        for pattern, tag in ((_BULLET, "ul"), (_NUMBER, "ol")):
            if pattern.match(line):
                items: list[str] = []
                while i < len(lines):
                    if m := pattern.match(lines[i]):
                        items.append(m.group(1).strip())
                        i += 1
                    elif lines[i].strip() and lines[i].startswith((" ", "\t")):
                        items[-1] += " " + lines[i].strip()   # a wrapped item
                        i += 1
                    else:
                        break
                body = "".join(f"<li>{inline(it)}</li>" for it in items)
                out.append(f"<{tag}>{body}</{tag}>")
                break
        else:
            para = []
            while i < len(lines):
                nxt = lines[i]
                if (not nxt.strip() or nxt.strip().startswith(("#", ">", "|"))
                        or nxt.strip() in ("---", "***", "___")
                        or _BULLET.match(nxt) or _NUMBER.match(nxt)):
                    break
                para.append(nxt.strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")

    return "\n".join(out)


def write(path: Path, title: str, description: str, body: str, home: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PAGE.format(title=html.escape(title),
                                description=html.escape(description, quote=True),
                                body=body, home=home), encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def main() -> None:
    for slug, title, description in DOCS:
        md = (ROOT / "source" / f"{slug}.md").read_text(encoding="utf-8")
        write(ROOT / slug / "index.html", title, description, render(md), home="../")

    cards = "".join(
        f'<li><a href="{slug}/">{title}</a><span>{html.escape(description)}</span></li>'
        for slug, title, description in DOCS)
    index = ("<h1>sanā</h1>"
             "<p>sanā plans and tracks training. It runs entirely on your device: "
             "there is no account, no server, and nothing is collected.</p>"
             f'<ul class="cards">{cards}</ul>'
             '<p>Questions: <a href="mailto:hello@entelana.com">hello@entelana.com</a></p>')
    write(ROOT / "index.html", "sanā", "Privacy policy and terms for sanā.", index, home="./")


if __name__ == "__main__":
    main()
