"""Predict denied requests. Fit on train, choose on dev, score test ONCE. Writes outputs/ml_results.json and outputs/scores.csv."""
import json, pathlib, sys
import duckdb, numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

ROOT = pathlib.Path(__file__).resolve().parent.parent
FEATS = ["resource", "mgr_id", "role_rollup_1", "role_rollup_2", "role_deptname", "role_title",
         "role_family_desc", "role_family", "role_code"]


def freq_encode(train, df):
    """Count-encode each ID with train counts (labels never used); also keeps the raw ID as a number."""
    out = pd.DataFrame(index=df.index)
    for c in FEATS:
        out[c + "_n"] = df[c].map(train[c].value_counts()).fillna(0)
        out[c] = df[c]
    return out


def run(db=ROOT / "data" / "access.duckdb", out=ROOT / "outputs", seed=42):
    df = duckdb.connect(str(db), read_only=True).execute("select * from requests").df()
    tr, dv, te = (df[df.split == s] for s in ("train", "dev", "test"))
    res = {"n": {k: int(len(v)) for k, v in (("train", tr), ("dev", dv), ("test", te))}, "denied_rate": float(df.denied.mean())}

    enc = OneHotEncoder(handle_unknown="ignore").fit(tr[FEATS])
    best = None
    for C in (0.03, 0.1, 0.3, 1.0):
        lr = LogisticRegression(C=C, max_iter=2000, class_weight="balanced").fit(enc.transform(tr[FEATS]), tr.denied)
        a = roc_auc_score(dv.denied, lr.predict_proba(enc.transform(dv[FEATS]))[:, 1])
        if best is None or a > best[0]: best = (a, C, lr)
    lr_dev, C, lr = best
    res["logreg"] = {"C": C, "dev_auc": lr_dev}

    Xtr, Xdv = freq_encode(tr, tr), freq_encode(tr, dv)
    rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=3, class_weight="balanced_subsample", n_jobs=-1, random_state=seed).fit(Xtr, tr.denied)
    res["random_forest"] = {"dev_auc": roc_auc_score(dv.denied, rf.predict_proba(Xdv)[:, 1])}

    # top drivers
    names = enc.get_feature_names_out(FEATS)
    coef = pd.Series(lr.coef_[0], index=names)
    cnt = pd.Series(np.asarray(enc.transform(tr[FEATS]).sum(axis=0)).ravel(), index=names)
    ok = coef[cnt >= 20]  # ignore values seen fewer than 20 times: too thin to call a driver
    res["logreg"]["top_risk_values"] = [{"feature": k, "coef": float(v)} for k, v in ok.nlargest(10).items()]
    res["logreg"]["top_safe_values"] = [{"feature": k, "coef": float(v)} for k, v in ok.nsmallest(10).items()]
    pi = permutation_importance(rf, Xdv, dv.denied, scoring="roc_auc", n_repeats=5, random_state=seed, n_jobs=-1)
    imp = pd.Series(pi.importances_mean, index=Xdv.columns)
    by_col = {c: float(imp[c] + imp[c + "_n"]) for c in FEATS}
    res["random_forest"]["permutation_importance_by_column"] = dict(sorted(by_col.items(), key=lambda kv: -kv[1]))

    # test scored ONCE, with the models chosen on dev
    res["logreg"]["test_auc"] = roc_auc_score(te.denied, lr.predict_proba(enc.transform(te[FEATS]))[:, 1])
    res["random_forest"]["test_auc"] = roc_auc_score(te.denied, rf.predict_proba(freq_encode(tr, te))[:, 1])

    scores = df[["request_id", "split"]].copy()
    scores["p_denied_lr"] = lr.predict_proba(enc.transform(df[FEATS]))[:, 1]
    scores["p_denied_rf"] = rf.predict_proba(freq_encode(tr, df))[:, 1]
    out.mkdir(exist_ok=True)
    scores.to_csv(out / "scores.csv", index=False)
    (out / "ml_results.json").write_text(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    r = run(); print(json.dumps({k: r[k] for k in ("logreg", "random_forest")}, indent=1)[:1800])
