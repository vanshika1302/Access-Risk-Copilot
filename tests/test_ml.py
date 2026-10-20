import json, pathlib
import duckdb, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_split_is_disjoint_stratified_and_complete():
    p = ROOT / "data" / "access.duckdb"
    df = duckdb.connect(str(p), read_only=True).execute("select split, count(*) n, avg(denied) r from requests group by 1").df().set_index("split")
    assert df.n.sum() == 32769
    assert abs(df.n["train"] / 32769 - 0.6) < 0.01
    assert df.r.max() - df.r.min() < 0.002  # stratified


def test_freq_encoding_uses_only_train_rows():
    from ml.train import freq_encode, FEATS
    tr = pd.DataFrame({c: [1, 1, 2] for c in FEATS})
    te = pd.DataFrame({c: [1, 3] for c in FEATS})
    enc = freq_encode(tr, te)
    assert list(enc["resource_n"]) == [2, 0]  # unseen id -> 0, never test counts


def test_results_report_both_models_with_sane_auc():
    r = json.loads((ROOT / "outputs" / "ml_results.json").read_text())
    for m in ("logreg", "random_forest"):
        assert 0.7 < r[m]["dev_auc"] < 1 and 0.7 < r[m]["test_auc"] < 1
    assert len(r["logreg"]["top_risk_values"]) == 10
