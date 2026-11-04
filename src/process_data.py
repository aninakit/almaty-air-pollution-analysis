"""Validate small benchmark logs and summarize successful evaluation attempts."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'data/raw/test_run.jsonl'
OUTPUT = ROOT / 'data/processed/metrics_summary.csv'
RANDOM_SEED = 42
BOOTSTRAP_SAMPLES = 10000

def load_data(path=INPUT, comparison=False):
    records = []
    with Path(path).open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'Invalid JSON at line {number}') from exc
                if not isinstance(record, dict):
                    raise ValueError(f'Expected an object at line {number}')
                records.append(record)
    df = pd.DataFrame(records)
    required = {'run_id', 'phase', 'latency_ms', 'success'}
    if comparison:
        required |= {'method', 'load_size', 'result'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(required - set(df.columns))}')
    if not df['phase'].isin(['warmup', 'evaluation']).all():
        raise ValueError('Unknown phase; expected warmup or evaluation')
    if not df['success'].map(lambda value: isinstance(value, bool)).all():
        raise ValueError('success must contain JSON booleans')
    latency = pd.to_numeric(df['latency_ms'], errors='raise')
    if not np.isfinite(latency).all() or (latency < 0).any():
        raise ValueError('Latency must be finite and nonnegative')
    df['latency_ms'] = latency
    ids = pd.to_numeric(df['run_id'], errors='raise')
    if not np.isfinite(ids).all() or (ids < 1).any() or (ids % 1 != 0).any():
        raise ValueError('run_id must be a positive integer')
    keys = ['run_id']
    if comparison:
        if not df['method'].isin(['Baseline', 'Proposed']).all():
            raise ValueError('Unknown comparison method')
        sizes = pd.to_numeric(df['load_size'], errors='raise')
        if not np.isfinite(sizes).all() or (sizes < 1).any() or (sizes % 1 != 0).any():
            raise ValueError('load_size must be a positive integer')
        df['load_size'] = sizes
        results = pd.to_numeric(df.loc[df['success'], 'result'], errors='raise')
        if not np.isfinite(results).all():
            raise ValueError('Successful method results must be finite')
        keys = ['method', 'load_size', 'run_id']
    if df.duplicated(keys).any():
        raise ValueError(f'Duplicate measurements for {keys}')
    return df

def bootstrap_ci(values, rng=None):
    values = np.asarray(values, dtype=float)
    if values.size < 2 or not np.isfinite(values).all():
        raise ValueError('At least two finite successful observations are required')
    if rng is None:
        rng = np.random.default_rng(RANDOM_SEED)
    means = [rng.choice(values, size=len(values), replace=True).mean()
             for _ in range(BOOTSTRAP_SAMPLES)]
    return np.percentile(means, [2.5, 97.5])

def summarize(df, rng=None):
    evaluation = df.loc[df['phase'] == 'evaluation']
    successful = evaluation.loc[evaluation['success']]
    values = successful['latency_ms'].to_numpy(dtype=float)
    low, high = bootstrap_ci(values, rng)
    return {
        'total_runs': len(df),
        'warmup_runs': int((df['phase'] == 'warmup').sum()),
        'evaluation_runs': len(evaluation),
        'successful_runs': len(successful),
        'error_rate_percent': (1 - len(successful) / len(evaluation)) * 100,
        'mean_ms': np.mean(values), 'median_ms': np.median(values),
        'std_ms': np.std(values, ddof=1),
        'p25_ms': np.percentile(values, 25), 'p75_ms': np.percentile(values, 75),
        'p95_ms': np.percentile(values, 95), 'p99_ms': np.percentile(values, 99),
        'ci95_lower_ms': low, 'ci95_upper_ms': high,
    }

def process_data():
    summary = summarize(load_data())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([summary]).to_csv(OUTPUT, index=False)
    print(pd.DataFrame([summary]).to_string(index=False))
    return summary

if __name__ == '__main__':
    process_data()
