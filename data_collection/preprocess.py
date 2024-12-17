import pandas as pd
import json
import datetime
import pytz
import sys
import os

# 현재 파일의 상위 디렉토리를 PYTHONPATH에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_collection.fetch_quantitative import fetch_30d_candlestick, fetch_current_price, fetch_24h_volume, fetch_5min_data

# 결측값 처리 함수
def handle_missing_values(data: pd.DataFrame, fill_value: float = 0.0) -> pd.DataFrame:
    """
    결측값을 지정된 값으로 대체합니다.
    :param data: DataFrame - 원본 데이터.
    :param fill_value: float - 결측값을 대체할 값, 기본값은 0.0.
    :return: DataFrame - 결측값이 처리된 데이터.
    """
    return data.fillna(fill_value)

# 데이터 정규화 함수
def normalize_data(data: pd.DataFrame, columns_to_keep: list = None) -> pd.DataFrame:
    """
    필요한 열만 유지합니다.
    :param data: DataFrame - 원본 데이터.
    :param columns_to_keep: list - 유지할 열 목록, 기본값은 ["close", "volume"].
    :return: DataFrame - 정규화된 데이터.
    """
    if columns_to_keep is None:
        columns_to_keep = ["close", "volume"]
    return data[columns_to_keep]

# 데이터 요약 추출 함수
def extract_relevant_data(data: pd.DataFrame, interval: int = 10) -> dict:
    """
    데이터를 구간별로 나눠 각 구간의 평균, 최고값, 최저값, 변동성을 계산하고 날짜 범위를 포함합니다.
    :param data: DataFrame - 정규화된 데이터.
    :param interval: int - 데이터를 나눌 구간(일수), 기본값은 10일.
    :return: dict - 구간별로 계산된 핵심 정보와 날짜 범위.
    """
    summary = {}
    num_intervals = len(data) // interval

    for i in range(num_intervals):
        start = i * interval
        end = start + interval
        segment = data.iloc[start:end]

        # 구간의 날짜 범위 계산
        start_date = segment.index.min()
        end_date = segment.index.max()

        summary[f"segment_{i + 1}"] = {
            "date_range": f"{start_date} to {end_date}",
            "average_price": segment["close"].mean(),
            "high_price": segment["close"].max(),
            "low_price": segment["close"].min(),
            "volatility": segment["close"].std(),
        }

    return summary

# JSON 변환 함수
def convert_to_json(data: dict) -> str:
    """
    데이터를 JSON 형식으로 변환합니다.
    :param data: dict - 변환할 데이터.
    :return: str - JSON 형식의 문자열.
    """
    return json.dumps(data, indent=4, ensure_ascii=False)

def preprocess_15min_data(data: pd.DataFrame) -> dict:
    """
    15분 봉 데이터를 전처리하여 구간별 통계 및 변동성을 계산합니다.
    :param data: DataFrame - 15분 봉 데이터.
    :return: dict - 전처리된 데이터 요약 정보.
    """
    if data is None or data.empty:
        return {"error": "No data available"}

    # 데이터 복사 및 15분 단위 구간 계산
    data = data.copy()
    data["time_index"] = (data.index - data.index[0]).total_seconds() // 900  # 15분 단위 (900초)

    # 15분 단위 통계 계산
    summary = {
        f"segment_15m_{int(idx) + 1}": {
            "avg_price": grp["close"].mean(),
            "high_price": grp["high"].max(),
            "low_price": grp["low"].min(),
            "volatility": grp["close"].std(),
            "vwap": (grp["close"] * grp["volume"]).sum() / grp["volume"].sum() if grp["volume"].sum() > 0 else 0,
            "total_vol": grp["volume"].sum(),
        }
        for idx, grp in data.groupby("time_index")
    }

    # 전체 분석 정보 추가
    summary["overall"] = {
        "trend": "up" if data["close"].iloc[-1] > data["close"].iloc[0] else "down",
        "max_volatility": round(data["close"].std(), 2),
        "outlier_count": len(
            data[
                (data["close"] > data["close"].mean() + 2 * data["close"].std()) |
                (data["close"] < data["close"].mean() - 2 * data["close"].std())
            ]
        ),  # 이상치 수만 포함
    }

    return summary

