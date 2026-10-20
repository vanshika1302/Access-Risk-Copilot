"""python scripts/resolve.py NN "answer" : mark ticket resolved, append answer and a pointer in map.md."""
import pathlib, re, sys
d = pathlib.Path(__file__).resolve().parent.parent / ".scratch" / "access-risk-copilot"
n, ans = sys.argv[1], sys.argv[2]
f = next((d / "issues").glob(f"{n}-*.md"))
t = f.read_text().replace("Status: open", "Status: resolved", 1).replace("Status: claimed", "Status: resolved", 1)
if "## Answer" not in t: t += f"\n## Answer\n{ans}\n"
f.write_text(t)
title = t.splitlines()[0].lstrip("# ")
m = (d / "map.md").read_text()
if f"issues/{f.name}" not in m:
    m = m.replace("\n## Not yet specified", f"- [{title}](issues/{f.name}): {ans}\n\n## Not yet specified", 1)
    (d / "map.md").write_text(m)
