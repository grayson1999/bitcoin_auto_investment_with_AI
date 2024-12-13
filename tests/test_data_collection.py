# tests/test_data_collection.py

import unittest
from unittest.mock import patch
import pandas as pd
from data_collection.fetch_quantitative import (
    fetch_current_price,
    fetch_24h_volume,
    fetch_30d_candlestick,
    fetch_5min_data,
)
from data_collection.preprocess import (
    handle_missing_values,
    normalize_data,
    extract_relevant_data,
    preprocess_5min_data,
)

class TestDataCollection(unittest.TestCase):

    @patch("data_collection.fetch_quantitative.get_current_price")
    def test_fetch_current_price(self, mock_get_current_price):
        """
        fetch_current_price 함수 테스트.
        """
        mock_get_current_price.return_value = 144575000.0
        result = fetch_current_price()
        self.assertEqual(result, 144575000.0)

    @patch("data_collection.fetch_quantitative.get_ohlcv")
    def test_fetch_24h_volume(self, mock_get_ohlcv):
        """
        fetch_24h_volume 함수 테스트.
        """
        mock_df = pd.DataFrame({
            "volume": [2153.7836404]
        })
        mock_get_ohlcv.return_value = mock_df
        result = fetch_24h_volume()
        self.assertEqual(result, 2153.7836404)

    @patch("data_collection.fetch_quantitative.get_ohlcv")
    def test_fetch_30d_candlestick(self, mock_get_ohlcv):
        """
        fetch_30d_candlestick 함수 테스트.
        """
        mock_df = pd.DataFrame({
            "open": [1000000],
            "high": [2000000],
            "low": [500000],
            "close": [1500000],
            "volume": [1000],
        })
        mock_get_ohlcv.return_value = mock_df
        result = fetch_30d_candlestick()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.iloc[0]["close"], 1500000)

    @patch("data_collection.fetch_quantitative.get_ohlcv")
    def test_fetch_5min_data(self, mock_get_ohlcv):
        """
        fetch_5min_data 함수 테스트.
        """
        mock_df = pd.DataFrame({
            "open": [1000000],
            "high": [2000000],
            "low": [500000],
            "close": [1500000],
            "volume": [100],
        })
        mock_get_ohlcv.return_value = mock_df
        result = fetch_5min_data()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.iloc[0]["close"], 1500000)

    def test_handle_missing_values(self):
        """
        handle_missing_values 함수 테스트.
        """
        data = pd.DataFrame({
            "close": [100, None, 200],
            "volume": [1.2, 3.4, None]
        })
        result = handle_missing_values(data, fill_value=0.0)
        self.assertEqual(result.isnull().sum().sum(), 0)

    def test_normalize_data(self):
        """
        normalize_data 함수 테스트.
        """
        data = pd.DataFrame({
            "close": [100, 200],
            "volume": [1.2, 3.4],
            "extra_col": [10, 20]
        })
        result = normalize_data(data)
        self.assertListEqual(list(result.columns), ["close", "volume"])

    def test_extract_relevant_data(self):
        """
        extract_relevant_data 함수 테스트.
        """
        data = pd.DataFrame({
            "close": [100, 200, 300, 400, 500, 600, 700],
            "volume": [1, 2, 3, 4, 5, 6, 7]
        })
        result = extract_relevant_data(data, interval=3)
        self.assertIn("segment_1", result)
        self.assertIn("average_price", result["segment_1"])

    def test_preprocess_5min_data(self):
        """
        preprocess_5min_data 함수 테스트.
        """
        data = pd.DataFrame({
            "open": [1000000, 1500000, 2000000],
            "high": [1200000, 1800000, 2200000],
            "low": [800000, 1400000, 1900000],
            "close": [1100000, 1700000, 2100000],
            "volume": [100, 200, 300]
        })
        data.index = pd.date_range(start="2024-12-13 00:00:00", periods=3, freq="5min")
        result = preprocess_5min_data(data)
        self.assertIn("hour_1", result)
        self.assertIn("average_price", result["hour_1"])

if __name__ == "__main__":
    unittest.main()
