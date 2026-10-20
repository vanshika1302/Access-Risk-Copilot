"""Controls run on a tiny hand-built warehouse so every expected flag is computed by hand."""
import duckdb, pandas as pd, pathlib

SQL = (pathlib.Path(__file__).resolve().parent.parent / "sql" / "controls.sql").read_text()


def make():
    rows = [  # request_id, resource, mgr_id, role_deptname, role_family, target, split
        (1, 10, 1, 7, 100, 1, "train"),  # SoD: mgr 1 resource 10, families 100 and 200 both approved
        (2, 10, 1, 7, 200, 1, "train"),
        (3, 10, 2, 7, 100, 1, "train"),  # same family only, no SoD
        (4, 10, 3, 7, 100, 1, "train"),  # other manager has 200 but denied -> no SoD
        (5, 10, 3, 7, 200, 0, "train"),
    ]
    df = pd.DataFrame(rows, columns=["request_id", "resource", "mgr_id", "role_deptname", "role_family", "target", "split"])
    df["denied"] = 1 - df["target"]
    con = duckdb.connect()
    con.execute("create table requests as select * from df")
    con.execute("create table sod_pairs as select 100 fam_a, 200 fam_b")
    con.execute(SQL)
    return con


def test_sod_flags_only_same_manager_same_resource_both_approved():
    ids = {r[0] for r in make().execute("select request_id from ctrl_sod").fetchall()}
    assert ids == {1, 2}


def test_unusual_needs_rare_pair():
    # resource 10 / dept 7 appears 5 times of 5 -> not rare
    assert make().execute("select count(*) from ctrl_unusual").fetchone()[0] == 0


def test_high_risk_uses_train_only_and_min_volume():
    assert make().execute("select count(*) from high_risk_resources").fetchone()[0] == 0  # n < 20


def test_real_warehouse_has_all_three_controls():
    p = pathlib.Path(__file__).resolve().parent.parent / "data" / "access.duckdb"
    if not p.exists():
        return
    con = duckdb.connect(str(p), read_only=True)
    got = {r[0] for r in con.execute("select distinct control from flags").fetchall()}
    assert got == {"SOD", "UNUSUAL", "HIGH_RISK_RESOURCE"}
