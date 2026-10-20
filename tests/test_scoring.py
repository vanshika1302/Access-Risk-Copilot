import copy
from ai.scoring import bucket, score, template_finding, errors

FACTS = {"request_id": 7, "ids": {"resource": 11, "mgr_id": 12, "role_deptname": 13, "role_family": 14, "role_title": 15},
         "controls": {"sod_conflict": True, "unusual_for_department": False, "high_risk_resource": False},
         "numbers": {"resource_requests": 40, "dept_requests": 200, "dept_resource_requests": 3, "risk_score_percentile": 80}}


def good():
    f = template_finding(FACTS); f["finding"] = "Request 7 has an SoD conflict; resource has 40 requests."; return f


def test_correct_finding_is_correct():
    assert bucket(FACTS, good()) == ("correct", [])


def test_wrong_claim_not_flagged_is_silent():
    f = good(); f["claims"]["sod_conflict"] = False
    assert bucket(FACTS, f)[0] == "SILENT"


def test_wrong_claim_flagged_uncertain_is_caught():
    f = good(); f["claims"]["high_risk_resource"] = True; f["uncertain"] = True
    assert bucket(FACTS, f)[0] == "caught"


def test_wrong_quoted_number_and_invented_text_number_are_errors():
    f = good(); f["quoted"]["resource_requests"] = 41
    assert "quoted:resource_requests" in errors(FACTS, f)
    f = good(); f["finding"] = "Resource has 99 requests."
    assert "text_number:99" in errors(FACTS, f)


def test_sod_policy_cannot_be_low_or_auto_approved():
    f = good(); f["severity"] = "low"
    assert any(e.startswith("policy") for e in errors(FACTS, f))


def test_score_rates():
    bad = {"request_id": 1, "facts": FACTS, "finding": {**good(), "claims": {**FACTS["controls"], "sod_conflict": False}}}
    ok = {"request_id": 2, "facts": FACTS, "finding": good()}
    s = score([bad, ok]); assert s["silent_error_rate"] == 0.5 and s["n"] == 2


def test_template_baseline_has_zero_errors():
    assert errors(FACTS, template_finding(FACTS)) == []
