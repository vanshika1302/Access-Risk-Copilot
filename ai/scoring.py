"""Score AI findings against SQL facts. Every case lands in one bucket:
correct | correct_flagged | caught (wrong but uncertain=true) | SILENT (wrong and uncertain=false)."""
import re

CLAIMS = ("sod_conflict", "unusual_for_department", "high_risk_resource")


def allowed_numbers(facts: dict) -> set[float]:
    nums = {float(facts["request_id"])}
    nums |= {float(v) for v in facts["ids"].values()} | {float(v) for v in facts["numbers"].values()}
    return nums


def errors(facts: dict, f: dict) -> list[str]:
    errs = []
    for c in CLAIMS:
        if f["claims"][c] != facts["controls"][c]: errs.append(f"claim:{c}")
    for k, v in f["quoted"].items():
        if v is not None and v != facts["numbers"][k]: errs.append(f"quoted:{k}")
    ok = allowed_numbers(facts)
    for m in re.findall(r"\d+(?:\.\d+)?", f["finding"]):
        if float(m) not in ok: errs.append(f"text_number:{m}")
    if facts["controls"]["sod_conflict"] and (f["severity"] == "low" or f["recommended_action"] == "approve_with_monitoring"):
        errs.append("policy:sod_must_not_be_low_or_auto_approved")
    return errs


def bucket(facts: dict, f: dict) -> tuple[str, list[str]]:
    e = errors(facts, f)
    if not e: return ("correct_flagged" if f["uncertain"] else "correct"), e
    return ("caught" if f["uncertain"] else "SILENT"), e


def score(items: list[dict]) -> dict:
    b = {"correct": 0, "correct_flagged": 0, "caught": 0, "SILENT": 0}; detail = []
    for it in items:
        k, e = bucket(it["facts"], it["finding"]); b[k] += 1
        if e: detail.append({"request_id": it["request_id"], "bucket": k, "errors": e})
    n = len(items)
    return {"n": n, "buckets": b, "silent_error_rate": b["SILENT"] / n if n else 0.0,
            "any_error_rate": (b["caught"] + b["SILENT"]) / n if n else 0.0,
            "catch_rate": b["caught"] / (b["caught"] + b["SILENT"]) if (b["caught"] + b["SILENT"]) else None, "error_cases": detail}


def template_finding(facts: dict) -> dict:
    """Rule-based baseline: fills a template from the facts. Correct by construction; it never explains anything new."""
    c, n = facts["controls"], facts["numbers"]
    hit = [k.replace("_", " ") for k, v in c.items() if v]
    sev = "high" if c["sod_conflict"] else "medium" if hit else "low"
    text = (f"Request {facts['request_id']}: " + ("; ".join(hit) if hit else "no control triggered") +
            f". Resource has {n['resource_requests']} requests; risk score percentile {n['risk_score_percentile']}.")
    return {"severity": sev, "finding": text, "claims": dict(c), "uncertain": False,
            "quoted": {k: n[k] for k in ("resource_requests", "dept_requests", "risk_score_percentile")},
            "recommended_action": "block_pending_review" if c["sod_conflict"] else "review_by_owner" if hit else "approve_with_monitoring"}
