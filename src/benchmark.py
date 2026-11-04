from pathlib import Path
import sys
import time
import logging
import yaml
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def check_sensor_coverage(df, limit):
    if df['sensor_id'].isna().any():
        raise ValueError("Missing sensor ID prevents per-sensor coverage checks")
    rates = df['pm25'].isna().groupby(df['sensor_id']).mean()
    failed = rates[rates > limit]
    if not failed.empty:
        raise ValueError(f"PM2.5 missing rate exceeds {limit:.0%} for {failed.to_dict()}")
    return rates


def run_benchmark():
    start_time = time.perf_counter()
    logging.info("Starting Almaty Air Quality Benchmark Pipeline...")

    # 1. Загрузка конфигурации
    config = load_config(ROOT / "configs/config.yaml")
    logging.info(f"Loaded configuration for experiment: {config['experiment']['name']}")

    # 2. Чтение тестового сэмпла данных
    data_path = config['data']['sample_path']
    df = pd.read_csv(ROOT / data_path)
    logging.info(f"Successfully loaded {len(df)} rows from '{data_path}'")

    # 3. Расчет первичных показателей (Primary Metrics)
    heating_pm25 = df[df['is_heating_season'] == 1]['pm25']
    non_heating_pm25 = df[df['is_heating_season'] == 0]['pm25']

    if heating_pm25.dropna().empty or non_heating_pm25.dropna().empty:
        raise ValueError("Both seasons must contain non-missing PM2.5 observations")
    mean_diff = heating_pm25.mean() - non_heating_pm25.mean()
    logging.info(f"[Primary Metric] Heating Season PM2.5 Mean Difference (Delta X): {mean_diff:.2f} ug/m3")

    # 4. Проверка Guardrail метрики (Missing Data Rate)
    limit = config['guardrails']['max_missing_data_rate']
    rates = check_sensor_coverage(df, limit)
    logging.info("PM2.5 missing rate by sensor: %s (limit %.0f%%)", rates.to_dict(), limit * 100)

    # 5. Замер времени исполнения (Latency)
    execution_time = (time.perf_counter() - start_time) * 1000
    logging.info(f"[Pipeline Metric] Benchmark Processing Latency: {execution_time:.2f} ms")
    logging.info("Benchmark execution completed successfully.")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler(ROOT / 'benchmark_results.log', mode='w')]
    )
    run_benchmark()
