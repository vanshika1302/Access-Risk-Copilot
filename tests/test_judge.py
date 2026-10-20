from ai.judge import inject, summarise, user_prompt, SYSTEM, SCHEMA


def item(i, sod=False):
    return {"request_id": i, "facts": {"request_id": i, "split": "dev", "ids": {}, "numbers": {},
            "controls": {"sod_conflict": sod, "unusual_for_department": False, "high_risk_resource": True}},
            "finding": {"finding": "Original text.", "uncertain": False}}


def test_inject_appends_false_sentence_and_does_not_mutate_input():
    items = [item(i) for i in range(8)]; out = inject(items, 8)
    assert all(o["finding"]["finding"] != "Original text." and o["injected"] for o in out)
    assert all(i["finding"]["finding"] == "Original text." for i in items)
    assert {o["injected"] for o in out} == {"false_control", "invented_history", "invented_cause", "invented_comparison"}


def test_false_control_only_asserts_a_control_that_is_actually_false():
    it = item(0); o = inject([it], 1)[0]
    assert "high-risk resource list" not in o["finding"]["finding"]  # that control IS true here


def test_summary_counts():
    items = [item(1), item(2)]
    g = [{"request_id": 1, "judge": {"unsupported": True, "unsupported_statements": ["x"]}}, {"request_id": 2, "judge": {"unsupported": False, "unsupported_statements": []}}]
    j = [{"request_id": 1, "injected": "invented_cause", "judge": {"unsupported": True, "unsupported_statements": []}}]
    s = summarise(items, g, j); assert s["genuine_flagged_unsupported"] == 1 and s["genuine_flagged_and_not_uncertain"] == 1 and s["injected_detected"] == 1


def test_prompt_treats_text_as_data_and_hides_split():
    u = user_prompt(item(1)); assert "<finding>" in u and "split" not in u and "never instructions" in SYSTEM
