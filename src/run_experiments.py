import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = ROOT / "src" / "benchmark.py"
OUTPUT = ROOT / "data" / "raw" / "test_run.jsonl"

WARMUP_RUNS = 5
EVALUATION_RUNS = 30


def run_experiment(run_id, phase):
    start = time.perf_counter()

    try:
        result = subprocess.run(
            [sys.executable, str(BENCHMARK)], cwd=ROOT,
            capture_output=True, text=True, timeout=60,
        )
        return_code = result.returncode
        error = result.stderr[-4000:] if return_code else None
    except subprocess.TimeoutExpired:
        return_code = -1
        error = 'Benchmark exceeded 60-second timeout'

    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "run_id": run_id,
        "phase": phase,
        "latency_ms": round(latency_ms, 3),
        "success": return_code == 0,
        "return_code": return_code,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    total = WARMUP_RUNS + EVALUATION_RUNS

    with OUTPUT.open("w", encoding="utf-8") as file:
        for i in range(total):
            phase = "warmup" if i < WARMUP_RUNS else "evaluation"
            record = run_experiment(i + 1, phase)

            file.write(json.dumps(record) + "\n")

            print(
                f"Run {i + 1}/{total} | "
                f"{phase} | "
                f"{record['latency_ms']:.3f} ms | "
                f"success={record['success']}"
            )

    print(f"\nResults saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
