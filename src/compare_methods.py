import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "sample" / "almaty_air_sample.csv"
OUTPUT = ROOT / "data" / "raw" / "method_comparison.jsonl"

LOAD_SIZES = [8, 80, 800, 8000]
WARMUP_RUNS = 5
EVALUATION_RUNS = 30


def baseline_method(df):
    """Baseline: row-by-row Python processing."""
    if not df["is_heating_season"].isin([0, 1]).all():
        raise ValueError("Season labels must be 0 or 1.")

    heating = []
    non_heating = []

    for _, row in df.iterrows():
        if pd.isna(row["pm25"]):
            continue
        if row["is_heating_season"] == 1:
            heating.append(row["pm25"])
        else:
            non_heating.append(row["pm25"])

    if not heating or not non_heating:
        raise ValueError("Both seasons must contain observations.")

    return float(np.mean(heating) - np.mean(non_heating))


def proposed_method(df):
    """Proposed: vectorized Pandas processing."""
    if not df["is_heating_season"].isin([0, 1]).all():
        raise ValueError("Season labels must be 0 or 1.")

    means = df.groupby("is_heating_season")["pm25"].mean()

    if 0 not in means.index or 1 not in means.index or means.loc[[0, 1]].isna().any():
        raise ValueError("Both seasons must contain observations.")

    return float(means.loc[1] - means.loc[0])


def measure(method, df, method_name, load_size, run_id, phase):
    start = time.perf_counter()
    success = True
    result = None
    error_message = None

    try:
        result = method(df)
    except Exception as exc:
        success = False
        error_message = str(exc)

    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "method": method_name,
        "load_size": load_size,
        "run_id": run_id,
        "phase": phase,
        "latency_ms": round(latency_ms, 6),
        "success": success,
        "result": result,
        "error": error_message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    original_df = pd.read_csv(DATA_PATH)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    methods = [
        ("Baseline", baseline_method),
        ("Proposed", proposed_method),
    ]

    total_records = 0

    with OUTPUT.open("w", encoding="utf-8") as file:
        for load_size in LOAD_SIZES:
            # Repeat original rows for synthetic load testing only
            repeats = int(np.ceil(load_size / len(original_df)))
            test_df = pd.concat(
                [original_df] * repeats,
                ignore_index=True
            ).iloc[:load_size].copy()

            # Check numerical equivalence
            baseline_result = baseline_method(test_df)
            proposed_result = proposed_method(test_df)

            if not np.isclose(
                baseline_result,
                proposed_result,
                rtol=1e-9,
                atol=1e-9
            ):
                raise ValueError(
                    f"Methods disagree at load size {load_size}"
                )

            print(f"\nLoad size: {load_size} rows")
            print(f"Correctness check: PASSED ({baseline_result:.4f})")

            for method_name, method in methods:
                for i in range(WARMUP_RUNS + EVALUATION_RUNS):
                    phase = (
                        "warmup"
                        if i < WARMUP_RUNS
                        else "evaluation"
                    )

                    record = measure(
                        method,
                        test_df,
                        method_name,
                        load_size,
                        i + 1,
                        phase
                    )

                    file.write(json.dumps(record) + "\n")
                    total_records += 1

                print(f"{method_name}: 35 runs completed")

    print(f"\nTotal records: {total_records}")
    print(f"Results saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
