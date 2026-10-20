"""Build dashboard/data.json, tableau/*.csv and index.html (from dashboard/template.html). Run: python scripts/export_dashboard.py"""
import json, pathlib, sys
import duckdb, numpy as np, pandas as pd
from sklearn.metrics import roc_curve

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build():
    con = duckdb.connect(str(ROOT / "data" / "access.duckdb"), read_only=True)
    req = con.execute("select * from requests").df()
    flags = con.execute("select request_id, control from flags").df()
    sc = pd.read_csv(ROOT / "outputs" / "scores.csv")
    ml = json.loads((ROOT / "outputs" / "ml_results.json").read_text())
    ev = json.loads((ROOT / "outputs" / "eval_results.json").read_text())

    wide = req.merge(sc[["request_id", "p_denied_lr", "p_denied_rf"]], on="request_id")
    for c in ("SOD", "UNUSUAL", "HIGH_RISK_RESOURCE"):
        wide["flag_" + c.lower()] = wide.request_id.isin(flags[flags.control == c].request_id).astype(int)
    wide["risk_percentile"] = (wide.p_denied_rf.rank(pct=True) * 100).round().astype(int)
    wide["risk_band"] = pd.cut(wide.risk_percentile, [-1, 79, 94, 100], labels=["Low (<80)", "Medium (80-94)", "High (95+)"])
    wide["outcome"] = np.where(wide.denied == 1, "Denied", "Approved")
    wide["model_scored_out_of_sample"] = (wide.split != "train").astype(int)
    wide.drop(columns=["target"]).to_csv(ROOT / "tableau" / "access_requests_scored.csv", index=False)

    held = wide[wide.split != "train"]   # dev + test: labels never used to build any control or model
    base = float(held.denied.mean())
    ctrl = []
    for c in ("SOD", "UNUSUAL", "HIGH_RISK_RESOURCE"):
        h = held[held["flag_" + c.lower()] == 1]
        ctrl.append({"control": c, "flagged_all": int(wide["flag_" + c.lower()].sum()), "flagged_held_out": int(len(h)),
                     "denial_rate": float(h.denied.mean()) if len(h) else None,
                     "lift": float(h.denied.mean() / base) if len(h) else None})
    te = wide[wide.split == "test"]
    roc = {}
    for k, col in (("logreg", "p_denied_lr"), ("random_forest", "p_denied_rf")):
        f, t, _ = roc_curve(te.denied, te[col]); idx = np.unique(np.linspace(0, len(f) - 1, 80).astype(int))
        roc[k] = [[round(float(f[i]), 4), round(float(t[i]), 4)] for i in idx]
    top = te.nlargest(int(len(te) * 0.05), "p_denied_rf")
    top5 = {"precision": float(top.denied.mean()), "recall": float(top.denied.sum() / te.denied.sum()), "n": int(len(top))}

    items = json.loads((ROOT / "outputs" / "findings_test.json").read_text())["items"]
    pick = {}
    for it in items:
        c = it["facts"]["controls"]; k = "sod_conflict" if c["sod_conflict"] else "high_risk_resource" if c["high_risk_resource"] else "unusual_for_department" if c["unusual_for_department"] else "model_only"
        pick.setdefault(k, []).append(it)
    examples = [{"kind": k, "request_id": v["request_id"], "facts": v["facts"]["controls"], "numbers": v["facts"]["numbers"], **{x: v["finding"][x] for x in ("severity", "finding", "uncertain", "recommended_action")}}
                for k, vs in pick.items() for v in vs[:3]]
    pd.DataFrame([{"request_id": it["request_id"], "split": "test", **it["facts"]["controls"], **it["facts"]["numbers"],
                   "severity": it["finding"]["severity"], "uncertain": it["finding"]["uncertain"],
                   "recommended_action": it["finding"]["recommended_action"], "finding": it["finding"]["finding"]} for it in items]
                 ).to_csv(ROOT / "tableau" / "ai_findings_test.csv", index=False)

    drivers = [{"name": k, "value": v} for k, v in ml["random_forest"]["permutation_importance_by_column"].items()]
    data = {"n_requests": int(len(wide)), "n_denied": int(wide.denied.sum()), "base_denial_rate": float(wide.denied.mean()),
            "held_out_denial_rate": base, "ml": {"logreg_test_auc": ml["logreg"]["test_auc"], "rf_test_auc": ml["random_forest"]["test_auc"],
            "logreg_dev_auc": ml["logreg"]["dev_auc"], "rf_dev_auc": ml["random_forest"]["dev_auc"]}, "roc": roc, "top5pct": top5,
            "drivers": drivers, "controls": ctrl,
            "eval": {s: {"n": ev[s]["claude"]["n"], "buckets": ev[s]["claude"]["buckets"], "silent_error_rate": ev[s]["claude"]["silent_error_rate"],
                         "baseline_buckets": ev[s]["template_baseline"]["buckets"]} for s in ("dev", "test")}, "examples": examples}
    (ROOT / "dashboard" / "data.json").write_text(json.dumps(data, indent=1))
    tpl = (ROOT / "dashboard" / "template.html").read_text()
    (ROOT / "index.html").write_text(tpl.replace("/*__DATA__*/null", json.dumps(data)))
    return data


if __name__ == "__main__":
    d = build(); print({k: d[k] for k in ("controls", "top5pct")})
