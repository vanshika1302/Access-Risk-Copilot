"""Dev score is free to repeat. The TEST score is written once: a second attempt is refused (same rule as Menu-Profit-Simulator).
python -m ai.evaluate            # score dev findings (and test findings if present and not yet scored)"""
import json, sys
from ai.facts import ROOT
from ai.scoring import score, template_finding

OUT = ROOT / "outputs" / "eval_results.json"


def run():
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    for split in ("dev", "test"):
        p = ROOT / "outputs" / f"findings_{split}.json"
        if not p.exists(): continue
        if split == "test" and "test" in res:
            print("test already scored once; refusing to rescore"); continue
        d = json.loads(p.read_text()); items = d["items"]
        res[split] = {"prompt_version": d["prompt_version"], "claude": score(items),
                      "template_baseline": score([{**i, "finding": template_finding(i["facts"])} for i in items])}
    OUT.write_text(json.dumps(res, indent=1)); return res


if __name__ == "__main__":
    r = run(); [print(s, {k: v for k, v in r[s]["claude"].items() if k != "error_cases"}) for s in r]
