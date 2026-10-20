"""Load the OpenML ARFF into a DuckDB warehouse (data/access.duckdb). Every column is an opaque anonymised ID."""
import pathlib, sys
import duckdb, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "amazon_access.arff"
DB = ROOT / "data" / "access.duckdb"
from etl.sod_pairs import pick_pairs  # noqa: E402

SEED = 42
COLS = ["resource", "mgr_id", "role_rollup_1", "role_rollup_2", "role_deptname", "role_title",
        "role_family_desc", "role_family", "role_code", "target"]


def read_arff(path=RAW) -> pd.DataFrame:
    lines = path.read_text().splitlines()
    start = lines.index("@data") + 1
    rows = [l.split(",") for l in lines[start:] if l.strip()]
    df = pd.DataFrame(rows, columns=COLS).astype(int)
    df.insert(0, "request_id", np.arange(1, len(df) + 1))
    return df


def add_split(df: pd.DataFrame) -> pd.DataFrame:
    """60/20/20 train/dev/test, stratified on the target, seed 42."""
    train, rest = train_test_split(df.index, test_size=0.4, stratify=df["target"], random_state=SEED)
    dev, test = train_test_split(rest, test_size=0.5, stratify=df.loc[rest, "target"], random_state=SEED)
    df = df.copy(); df["split"] = "train"; df.loc[dev, "split"] = "dev"; df.loc[test, "split"] = "test"
    df["denied"] = 1 - df["target"]   # target 1 = approved (Kaggle ACTION)
    return df


def build(db=DB, raw=RAW):
    df = add_split(read_arff(raw))
    con = duckdb.connect(str(db))
    con.execute("create or replace table requests as select * from df")
    fams = [r[0] for r in con.execute("select role_family from requests group by 1 order by count(*) desc, 1").fetchall()]
    pairs = pd.DataFrame(pick_pairs(fams), columns=["fam_a", "fam_b"])
    con.execute("create or replace table sod_pairs as select * from pairs")
    for f in sorted((ROOT / "sql").glob("*.sql")):
        con.execute(f.read_text())
    con.close()
    return df


if __name__ == "__main__":
    d = build(); print(len(d), d["split"].value_counts().to_dict(), "denied", int(d["denied"].sum()))
