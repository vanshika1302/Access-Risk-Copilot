"""Tiny Kanban view of the wayfinder map: python scripts/board.py  (serves on a free localhost port)."""
import html, http.server, pathlib, re, socketserver, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / ".scratch" / "access-risk-copilot" / "issues"


def tickets():
    out = []
    for f in sorted(ROOT.glob("*.md")):
        t = f.read_text()
        title = t.splitlines()[0].lstrip("# ")
        g = lambda k: (re.search(rf"^{k}: *(.*)$", t, re.M) or [None, ""])[1]
        out.append((title, g("Type"), g("Status"), g("Blocked by")))
    return out


def page():
    ts = tickets()
    done = {t[0].split()[0] for t in ts if t[2] == "resolved"}
    cols = {"Blocked": [], "Frontier": [], "Claimed": [], "Resolved": []}
    for title, typ, st, blk in ts:
        deps = [b.strip() for b in blk.split(",") if b.strip()]
        if st == "resolved": c = "Resolved"
        elif st == "claimed": c = "Claimed"
        elif all(d in done for d in deps): c = "Frontier"
        else: c = "Blocked"
        cols[c].append(f"<div class=card><b>{html.escape(title)}</b><br><small>{html.escape(typ)}"
                       f"{' · blocked by ' + html.escape(blk) if blk and c == 'Blocked' else ''}</small></div>")
    body = "".join(f"<section><h2>{k} ({len(v)})</h2>{''.join(v)}</section>" for k, v in cols.items())
    return ("<meta charset=utf-8><title>Map board</title><style>body{font:14px system-ui;background:#f4f5f7;display:flex;gap:12px;padding:16px}"
            "section{flex:1;background:#e4e6ea;border-radius:8px;padding:8px}.card{background:#fff;border-radius:6px;padding:8px;margin:6px 0;box-shadow:0 1px 2px #0003}"
            f"h2{{font-size:14px}}</style>{body}").encode()


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers(); self.wfile.write(page())
    def log_message(self, *a): pass


if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", 0), H) as s:
        print(f"board at http://127.0.0.1:{s.server_address[1]}", flush=True)
        s.serve_forever()
