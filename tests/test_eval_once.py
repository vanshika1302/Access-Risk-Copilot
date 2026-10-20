import json, pathlib
from ai import evaluate

R = pathlib.Path(__file__).resolve().parent.parent / "outputs" / "eval_results.json"


def test_test_split_is_scored_once_and_not_overwritten(capsys):
    before = json.loads(R.read_text())["test"]
    evaluate.run()
    assert json.loads(R.read_text())["test"] == before
    assert "refusing to rescore" in capsys.readouterr().out


def test_committed_results_have_expected_sizes():
    r = json.loads(R.read_text())
    assert r["dev"]["claude"]["n"] == 77 and r["test"]["claude"]["n"] == 60
    assert sum(r["test"]["claude"]["buckets"].values()) == 60
