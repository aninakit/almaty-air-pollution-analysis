"""Almaty city-day PM2.5 observations and a separate, measured workload."""
import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

if __package__:
    from .compare_methods import baseline_method, proposed_method, measure
    from .process_comparison import summarize_comparison
    from .process_data import load_data
else:
    from compare_methods import baseline_method, proposed_method, measure
    from process_comparison import summarize_comparison
    from process_data import load_data

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://raw.githubusercontent.com/qazybekb/AirDatakz-OpenData/5046605280f4a98e22a3e9bf6b06759db797d51f/almaty/daily/pm25.csv.gz'
SNAPSHOT = ROOT / 'data/environment/almaty_daily_pm25.csv'
LOG = ROOT / 'data/raw/observed_days.jsonl'
OUT = ROOT / 'data/processed'
COLUMNS = ['date', 'value_ugm3', 'n_clusters', 'n_stations']


def extract(compressed):
    df = pd.read_csv(io.BytesIO(compressed), compression='gzip', usecols=COLUMNS)
    subset = df.loc[df.date.between('2021-01-01', '2025-12-31'), COLUMNS]
    return subset.sort_values('date').to_csv(index=False, lineterminator='\n').encode()


def load_days():
    df = pd.read_csv(SNAPSHOT, parse_dates=['date'])
    if df.empty or df.date.duplicated().any() or df[COLUMNS].isna().any().any():
        raise ValueError('Expected unique, complete city-day records')
    if not (df.value_ugm3.ge(0) & np.isfinite(df.value_ugm3)
            & df.n_clusters.ge(1) & df.n_stations.ge(df.n_clusters)
            & df.date.dt.year.between(2021, 2025)).all():
        raise ValueError('Invalid date, concentration or reporting coverage')
    df['season'] = df.date.dt.month.map({12:'winter', 1:'winter', 2:'winter',
                                        6:'summer', 7:'summer', 8:'summer'})
    return df


def seasonal_summary(df):
    groups = df.dropna(subset=['season']).groupby([df.date.dt.year.rename('year'), 'season'])
    result = groups.value_ugm3.agg(['count', 'mean']).unstack()
    result.columns = ['_'.join(pair) for pair in result.columns]
    result['winter_minus_summer_ugm3'] = result.mean_winter - result.mean_summer
    return result


def workload(df):
    days = df.dropna(subset=['season'])
    return pd.DataFrame({'pm25': days.value_ugm3,
                         'is_heating_season': days.season.eq('winter').astype(int)})


def collect(frame):
    methods = [('Baseline', baseline_method), ('Proposed', proposed_method)]
    records = []
    for run in range(1, 36):
        for name, method in methods[::1 if run % 2 else -1]:
            records.append(measure(method, frame, name, len(frame), run,
                                   'warmup' if run <= 5 else 'evaluation'))
    LOG.write_text(''.join(json.dumps(row) + '\n' for row in records), encoding='utf8')


def analyze():
    days = load_days()
    frame = workload(days)
    value = proposed_method(frame)
    assert np.isclose(baseline_method(frame), value)
    log = load_data(LOG, comparison=True)
    ok = log[log.success]
    if not log.load_size.eq(len(frame)).all() or not np.allclose(ok.result, value):
        raise ValueError('Performance log does not match the observed workload')
    seasonal = seasonal_summary(days)
    perf = summarize_comparison(log)
    OUT.mkdir(exist_ok=True)
    seasonal.to_csv(OUT / 'observed_seasons.csv')
    perf.to_csv(OUT / 'observed_method_summary.csv', index=False)
    return seasonal, perf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-source', action='store_true')
    parser.add_argument('--collect', action='store_true')
    args = parser.parse_args()
    if args.verify_source:
        with urlopen(SOURCE, timeout=120) as response:
            expected = extract(response.read())
        if SNAPSHOT.read_bytes().replace(b'\r\n', b'\n') != expected:
            raise ValueError('Snapshot differs from pinned source')
        print('Verified snapshot SHA-256:', hashlib.sha256(expected).hexdigest())
    if args.collect:
        collect(workload(load_days()))
    for table in analyze():
        print(table.to_string())
