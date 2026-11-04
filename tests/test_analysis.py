import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src.process_data import load_data, summarize, bootstrap_ci
from src.compare_methods import baseline_method, proposed_method

class AnalysisTests(unittest.TestCase):
    def test_bad_sensor_is_detected_even_when_overall_coverage_passes(self):
        from src.benchmark import check_sensor_coverage
        sample = pd.DataFrame({'sensor_id': ['A'] * 8 + ['B'] * 2,
                               'pm25': [10.0] * 9 + [np.nan]})
        self.assertLess(sample.pm25.isna().mean(), 0.15)
        with self.assertRaisesRegex(ValueError, 'B'):
            check_sensor_coverage(sample, 0.15)

    def test_warmup_and_failure_denominators(self):
        df = pd.DataFrame([
            {'phase': 'warmup', 'success': True, 'latency_ms': 99999},
            {'phase': 'evaluation', 'success': True, 'latency_ms': 1},
            {'phase': 'evaluation', 'success': True, 'latency_ms': 3},
            {'phase': 'evaluation', 'success': False, 'latency_ms': 5000},
        ])
        result = summarize(df)
        self.assertEqual(result['evaluation_runs'], 3)
        self.assertEqual(result['successful_runs'], 2)
        self.assertAlmostEqual(result['error_rate_percent'], 100 / 3)
        self.assertEqual(result['mean_ms'], 2)
        self.assertEqual(result['median_ms'], 2)
        self.assertAlmostEqual(result['std_ms'], np.sqrt(2))
        self.assertAlmostEqual(result['p95_ms'], 2.9)
        self.assertAlmostEqual(result['p99_ms'], 2.98)

    def test_reproducible_bootstrap_and_insufficient_data(self):
        np.testing.assert_array_equal(bootstrap_ci([1, 2, 7]), bootstrap_ci([1, 2, 7]))
        np.testing.assert_array_equal(bootstrap_ci([5, 5]), [5, 5])
        for values in ([], [1], [1, float('nan')]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                bootstrap_ci(values)

    def test_methods_agree_with_missing_values(self):
        df = pd.DataFrame({'is_heating_season': [0, 0, 1, 1],
                           'pm25': [1, np.nan, 4, 6]})
        self.assertEqual(baseline_method(df), 4)
        self.assertEqual(proposed_method(df), 4)
        for method in (baseline_method, proposed_method):
            for frame in (df[df.is_heating_season == 0],
                          pd.DataFrame({'is_heating_season': [0, 2], 'pm25': [1, 5]})):
                with self.subTest(method=method.__name__), self.assertRaises(ValueError):
                    method(frame)

    def test_bad_log_values_are_rejected(self):
        record = {'run_id': 1, 'phase': 'evaluation', 'success': True, 'latency_ms': 1}
        mutations = [{'success': 'false'}, {'phase': 'eval'}, {'latency_ms': -1},
                     {'latency_ms': float('nan')}, {'run_id': 0}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'runs.jsonl'
            for mutation in mutations:
                path.write_text(json.dumps({**record, **mutation}) + '\n', encoding='utf-8')
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    load_data(path)
            path.write_text((json.dumps(record) + '\n') * 2, encoding='utf-8')
            with self.assertRaises(ValueError):
                load_data(path)

if __name__ == '__main__':
    unittest.main()
