"""Claude Code headless client (no API key). Every call: all tools disabled, no skills/MCP/settings, empty cwd, API keys removed from env."""
import hashlib, json, os, pathlib, subprocess, tempfile

MODEL = "claude-sonnet-5-5"
REC = pathlib.Path(__file__).resolve().parent.parent / "data" / "recordings"


class LiveNotAllowed(RuntimeError): pass


def command(system: str, schema: dict, model: str = MODEL) -> list[str]:
    return ["claude", "-p", "--output-format", "json", "--tools", "", "--disable-slash-commands", "--strict-mcp-config",
            "--no-session-persistence", "--setting-sources", "", "--system-prompt", system, "--model", model,
            "--json-schema", json.dumps(schema)]


def key(system: str, user: str, schema: dict, model: str = MODEL) -> str:
    return hashlib.sha256(json.dumps([system, user, schema, model], sort_keys=True).encode()).hexdigest()[:24]


def complete_json(system, user, schema, live=False, model=MODEL, rec_dir=REC, timeout=90):
    """Replay a recording if present; otherwise (only with live=True) call claude -p and record the answer."""
    rec_dir = pathlib.Path(rec_dir); f = rec_dir / f"claude-code_{model}_{key(system, user, schema, model)}.json"
    if f.exists(): return json.loads(f.read_text())["output"]
    if not live: raise LiveNotAllowed(f"no recording {f.name}; re-run with --live")
    if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("CI"): raise LiveNotAllowed("no live calls under tests or CI")
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL")}
    last = ""
    for _ in range(3):
        with tempfile.TemporaryDirectory(prefix="arc_cc_") as cwd:
            try:
                p = subprocess.run(command(system, schema, model), input=user, capture_output=True, text=True, cwd=cwd, env=env, timeout=timeout)
            except subprocess.TimeoutExpired:
                last = f"timed out after {timeout}s"; continue
        try:
            out = json.loads(p.stdout)
        except json.JSONDecodeError:
            last = p.stderr[:300] or f"exit {p.returncode}"; continue
        if out.get("permission_denials"): raise RuntimeError(f"tool request denied: {out['permission_denials']}")
        if out.get("is_error") or out.get("structured_output") is None:
            last = str(out.get("result"))[:300]; continue
        rec_dir.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"model": model, "output": out["structured_output"]}, indent=1))
        return out["structured_output"]
    raise RuntimeError(f"claude -p failed 3 times: {last}")
