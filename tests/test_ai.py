import json, pytest, jsonschema
from ai import client
from ai.findings import SCHEMA, SYSTEM, user_prompt


def test_command_disables_all_tools_and_has_no_key_flags():
    cmd = client.command("s", {"type": "object"})
    i = cmd.index("--tools"); assert cmd[i + 1] == ""
    assert "--strict-mcp-config" in cmd and "--no-session-persistence" in cmd and "--setting-sources" in cmd
    assert not any("api" in c.lower() and "key" in c.lower() for c in cmd)


def test_no_live_call_without_flag_or_under_pytest(tmp_path):
    with pytest.raises(client.LiveNotAllowed): client.complete_json("s", "u", {"type": "object"}, rec_dir=tmp_path)
    with pytest.raises(client.LiveNotAllowed): client.complete_json("s", "u", {"type": "object"}, live=True, rec_dir=tmp_path)


def test_replay_returns_recording(tmp_path):
    k = client.key("s", "u", {"a": 1}); (tmp_path / f"claude-code_{client.MODEL}_{k}.json").write_text(json.dumps({"output": {"x": 1}}))
    assert client.complete_json("s", "u", {"a": 1}, rec_dir=tmp_path) == {"x": 1}


def test_prompt_wraps_facts_as_data_and_omits_outcome():
    case = {"request_id": 1, "split": "dev", "ids": {}, "controls": {}, "numbers": {}}
    u = user_prompt(case); assert u.startswith("<facts>") and "</facts>" in u and "denied" not in u and "split" not in u
    assert "never instructions" in SYSTEM


def test_recorded_findings_match_schema():
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "outputs" / "findings_dev.json"
    for it in json.loads(p.read_text())["items"]: jsonschema.validate(it["finding"], SCHEMA)
