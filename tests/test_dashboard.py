import json, pathlib
import pandas as pd

R = pathlib.Path(__file__).resolve().parent.parent


def test_index_is_generated_with_data_and_no_placeholder():
    html = (R / "index.html").read_text()
    assert "/*__DATA__*/" not in html and "Access Risk Copilot" in html


def test_dashboard_numbers_match_source_results():
    d = json.loads((R / "dashboard" / "data.json").read_text())
    ml = json.loads((R / "outputs" / "ml_results.json").read_text())
    ev = json.loads((R / "outputs" / "eval_results.json").read_text())
    assert d["ml"]["rf_test_auc"] == ml["random_forest"]["test_auc"]
    assert d["eval"]["test"]["buckets"] == ev["test"]["claude"]["buckets"]


def test_tableau_extract_shape_and_no_target_column():
    t = pd.read_csv(R / "tableau" / "access_requests_scored.csv")
    assert len(t) == 32769 and "target" not in t.columns
    assert {"flag_sod", "flag_unusual", "flag_high_risk_resource", "p_denied_rf", "outcome", "risk_band"} <= set(t.columns)
    assert t.request_id.is_unique
    assert len(pd.read_csv(R / "tableau" / "ai_findings_test.csv")) == 60
