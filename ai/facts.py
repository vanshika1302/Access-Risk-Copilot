"""SQL facts for each case: what the controls and the model actually say. The AI layer sees these; the scorer checks it against them."""
import json, pathlib, random
import duckdb, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "access.duckdb"
SEED = 42
QUOTAS = {"dev": {"SOD": 15, "HIGH_RISK_RESOURCE": 25, "UNUSUAL": 25, "MODEL_ONLY": 15},
          "test": {"SOD": 12, "HIGH_RISK_RESOURCE": 18, "UNUSUAL": 18, "MODEL_ONLY": 12}}


def all_facts(db=DB, scores=ROOT / "outputs" / "scores.csv") -> pd.DataFrame:
    con = duckdb.connect(str(db), read_only=True)
    r = con.execute("select * from requests").df()
    f = con.execute("select request_id, control, detail from flags").df()
    for c in ("SOD", "UNUSUAL", "HIGH_RISK_RESOURCE"):
        r[c.lower()] = r.request_id.isin(f[f.control == c].request_id)
    r["resource_requests"] = r.groupby("resource").request_id.transform("count")
    r["dept_requests"] = r.groupby("role_deptname").request_id.transform("count")
    r["dept_resource_requests"] = r.groupby(["role_deptname", "resource"]).request_id.transform("count")
    s = pd.read_csv(scores)[["request_id", "p_denied_rf"]]
    r = r.merge(s, on="request_id")
    r["risk_percentile"] = (r.p_denied_rf.rank(pct=True) * 100).round().astype(int)
    return r


def primary(row) -> str:
    for c in ("SOD", "HIGH_RISK_RESOURCE", "UNUSUAL"):
        if row[c.lower()]: return c
    return "MODEL_ONLY"


def sample_cases(split: str, df: pd.DataFrame | None = None) -> list[dict]:
    """Stratified, seeded sample of flagged cases (plus model-only high scorers with no control flag)."""
    df = all_facts() if df is None else df
    d = df[df.split == split].copy()
    d["primary"] = d.apply(primary, axis=1)
    # MODEL_ONLY pool: no control flag, risk percentile >= 95
    d = d[(d.primary != "MODEL_ONLY") | (d.risk_percentile >= 95)]
    out = []
    for key, n in QUOTAS[split].items():
        pool = d[d.primary == key].sort_values("request_id")
        out += pool.sample(min(n, len(pool)), random_state=SEED).to_dict("records")
    random.Random(SEED).shuffle(out)
    return [facts_packet(r) for r in out]


def facts_packet(r: dict) -> dict:
    """The only thing the model sees. IDs are anonymised; no outcome label is included."""
    return {"request_id": int(r["request_id"]), "split": r["split"],
            "ids": {k: int(r[k]) for k in ("resource", "mgr_id", "role_deptname", "role_family", "role_title")},
            "controls": {"sod_conflict": bool(r["sod"]), "unusual_for_department": bool(r["unusual"]),
                         "high_risk_resource": bool(r["high_risk_resource"])},
            "numbers": {"resource_requests": int(r["resource_requests"]), "dept_requests": int(r["dept_requests"]),
                        "dept_resource_requests": int(r["dept_resource_requests"]),
                        "risk_score_percentile": int(r["risk_percentile"])}}


if __name__ == "__main__":
    for s in ("dev", "test"):
        c = sample_cases(s); (ROOT / "outputs" / f"cases_{s}.json").write_text(json.dumps(c, indent=1)); print(s, len(c))
