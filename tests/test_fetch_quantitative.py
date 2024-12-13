# tests/test_fetch_quantitative.py

import unittest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_collection.fetch_quantitative import fetch_current_price, fetch_24h_volume, fetch_30d_candlestick
import pandas as pd

class TestFetchQuantitative(unittest.TestCase):

    @patch("data_collection.fetch_quantitative.get_current_price")
    def test_fetch_current_price(self, mock_get_current_price):
        """
        fetch_current_price 함수 테스트.
        모의된 현재 가격 데이터를 반환하는지 확인.
        """
        mock_get_current_price.return_value = 50000000.0

        result = fetch_current_price()
        self.assertEqual(result, 50000000.0)

    @patch("data_collection.fetch_quantitative.get_ohlcv")
    def test_fetch_24h_volume(self, mock_get_ohlcv):
        """
        fetch_24h_volume 함수 테스트.
        모의된 24시간 거래량 데이터를 반환하는지 확인.
        """
        mock_df = pd.DataFrame({
            "volume": [12345.67]
        })
        mock_get_ohlcv.return_value = mock_df

        result = fetch_24h_volume()
        self.assertEqual(result, 12345.67)

    @patch("data_collection.fetch_quantitative.get_ohlcv")
    def test_fetch_30d_candlestick(self, mock_get_ohlcv):
        """
        fetch_30d_candlestick 함수 테스트.
        모의된 30일 일봉 데이터를 DataFrame 형태로 반환하는지 확인.
        """
        mock_df = pd.DataFrame({
            "candle_date_time_utc": ["2024-12-01T00:00:00"],
            "opening_price": [48000000.0],
            "trade_price": [50000000.0],
            "high_price": [51000000.0],
            "low_price": [47000000.0]
        })
        mock_get_ohlcv.return_value = mock_df

        result = fetch_30d_candlestick()
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["trade_price"], 50000000.0)

if __name__ == "__main__":
    unittest.main()
