import sys
import time
import logging
import yaml
import pandas as pd
import numpy as np

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("benchmark_results.log", mode='w')
    ]
)

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_benchmark():
    start_time = time.time()
    logging.info("Starting Almaty Air Quality Benchmark Pipeline...")

    # 1. Загрузка конфигурации
    config = load_config("configs/config.yaml")
    logging.info(f"Loaded configuration for experiment: {config['experiment']['name']}")

    # 2. Чтение тестового сэмпла данных
    data_path = config['data']['sample_path']
    df = pd.read_csv(data_path)
    logging.info(f"Successfully loaded {len(df)} rows from '{data_path}'")

    # 3. Расчет первичных показателей (Primary Metrics)
    heating_pm25 = df[df['is_heating_season'] == 1]['pm25']
    non_heating_pm25 = df[df['is_heating_season'] == 0]['pm25']

    mean_diff = heating_pm25.mean() - non_heating_pm25.mean()
    logging.info(f"[Primary Metric] Heating Season PM2.5 Mean Difference (Delta X): {mean_diff:.2f} ug/m3")

    # 4. Проверка Guardrail метрики (Missing Data Rate)
    missing_rate = df['pm25'].isnull().mean()
    max_missing_allowed = config['guardrails']['max_missing_data_rate']
    logging.info(f"[Guardrail Metric] Missing Data Rate (MDR): {missing_rate:.2%} (Limit: {max_missing_allowed:.0%})")
    
    if missing_rate <= max_missing_allowed:
        logging.info("Guardrail check PASSED: Missing Data Rate is within safe limits.")
    else:
        logging.warning("Guardrail check FAILED: High missing data rate detected!")

    # 5. Замер времени исполнения (Latency)
    execution_time = (time.time() - start_time) * 1000
    logging.info(f"[Pipeline Metric] Benchmark Processing Latency: {execution_time:.2f} ms")
    logging.info("Benchmark execution completed successfully.")

if __name__ == "__main__":
    run_benchmark()
