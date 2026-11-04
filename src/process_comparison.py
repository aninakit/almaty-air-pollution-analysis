"""Aggregate method timings using the same statistics as the process benchmark."""
from pathlib import Path
import numpy as np
import pandas as pd
try:
    from .process_data import load_data, summarize, RANDOM_SEED
except ImportError:
    from process_data import load_data, summarize, RANDOM_SEED

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / 'data/raw/method_comparison.jsonl'
OUTPUT = ROOT / 'data/processed/method_comparison_summary.csv'

def summarize_comparison(df):
    rng = np.random.default_rng(RANDOM_SEED)
    records = []
    for (method, size), group in df.groupby(['method', 'load_size']):
        records.append({'method': method, 'load_size': size, **summarize(group, rng)})
    return pd.DataFrame(records).sort_values(['load_size', 'method']).reset_index(drop=True)

def main():
    summary = summarize_comparison(load_data(INPUT, comparison=True))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUT, index=False)
    print(summary.to_string(index=False))
    return summary

if __name__ == '__main__':
    main()
