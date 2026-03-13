import argparse
import json
import os
import pandas as pd

def load_static_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_dynamic_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--static-json", required=True, help="Static features JSON from static_features.py --json-out")
    ap.add_argument("--dynamic-json", required=True, help="Dynamic features JSON saved from procmon_features.py output")
    ap.add_argument("--label", required=True, type=int, choices=[0,1], help="0=benign, 1=malware")
    ap.add_argument("--out-csv", default="dataset/fused_features.csv", help="Output CSV to append to")
    args = ap.parse_args()

    s = load_static_json(args.static_json)
    d = load_dynamic_json(args.dynamic_json)

    # Drop identifiers from static
    for k in ["path", "filename", "sha256"]:
        s.pop(k, None)

    row = {}
    row.update(s)
    row.update(d)
    row["label"] = args.label

    df_row = pd.DataFrame([row])

    out_csv = args.out_csv
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    if os.path.exists(out_csv):
        df_row.to_csv(out_csv, mode="a", header=False, index=False)
    else:
        df_row.to_csv(out_csv, mode="w", header=True, index=False)

    print(f"[OK] Appended 1 row to {out_csv}")
    print(df_row.to_string(index=False))

if __name__ == "__main__":
    main()