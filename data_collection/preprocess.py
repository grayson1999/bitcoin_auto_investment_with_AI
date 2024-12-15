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

def preprocess_5min_data(data: pd.DataFrame) -> dict:
    """
    5분 봉 데이터를 전처리하여 구간별 통계 및 변동성을 계산합니다.
    :param data: DataFrame - 5분 봉 데이터.
    :return: dict - 전처리된 데이터 요약 정보.
    """
    if data is None or data.empty:
        return {"error": "No data available"}

    # 시간 구간 계산
    data = data.copy()
    data["time_index"] = (data.index - data.index[0]).total_seconds() // 3600  # 1시간 단위

    # 시간별 통계 계산
    summary = {
        f"hour_{int(idx) + 1}": {
            "avg_price": grp["close"].mean(),
            "high_price": grp["high"].max(),
            "low_price": grp["low"].min(),
            "volatility": grp["close"].std(),
            "vwap": (grp["close"] * grp["volume"]).sum() / grp["volume"].sum(),
            "total_vol": grp["volume"].sum(),
        }
        for idx, grp in data.groupby("time_index")
    }

    # 전체 분석 최적화
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



def filter_bitcoin_portfolio(portfolio: dict, target_currency: str = "BTC") -> dict:
    """
    포트폴리오에서 특정 코인의 정보만 필터링합니다.
    :param portfolio: dict - 전체 포트폴리오 상태.
    :param target_currency: str - 대상 코인 (기본값은 'BTC').
    :return: dict - 현금 잔고와 대상 코인 정보만 포함된 포트폴리오.
    """
    try:
        filtered_portfolio = {"cash_balance": portfolio["cash_balance"], "target_asset": {"currency": target_currency, "balance": 0.0, "avg_buy_price": 0.0}}

        for asset in portfolio["invested_assets"]:
            if asset["currency"] == target_currency:
                filtered_portfolio["target_asset"] = asset
                break

        return filtered_portfolio
    except Exception as e:
        print(f"포트폴리오 필터링 중 오류 발생: {e}")
        return {"error": f"An error occurred while filtering the portfolio: {e}"}


if __name__ == "__main__":
    try:
        # 아시아 서울 시간 (UTC+9) 가져오기
        seoul_tz = pytz.timezone("Asia/Seoul")
        current_datetime = datetime.datetime.now(seoul_tz).isoformat()
        
        # 현재 가격 확인
        current_price = fetch_current_price()
        print(f"현재 비트코인 가격: {current_price}")

        # 24시간 거래량 확인
        volume_24h = fetch_24h_volume()
        print(f"24시간 거래량: {volume_24h}")

        # 30일 일봉 데이터 처리
        candlestick_30d = fetch_30d_candlestick()
        if candlestick_30d is not None:
            print("최근 30일 일봉 데이터:")
            cleaned_30d = handle_missing_values(candlestick_30d)
            normalized_30d = normalize_data(cleaned_30d)
            summary_30d = extract_relevant_data(normalized_30d, interval=7)
            print("30일 일봉 데이터 요약:")
            print(summary_30d)
        else:
            summary_30d = {"error": "Failed to fetch 30-day candlestick data"}

        # 3시간 5분 봉 데이터 처리
        raw_5min_data = fetch_5min_data()
        if raw_5min_data is not None:
            print("최근 3시간 5분 봉 데이터:")
            cleaned_5min = handle_missing_values(raw_5min_data)
            processed_5min = preprocess_5min_data(cleaned_5min)
            print("5분 봉 데이터 요약:")
            print(processed_5min)
        else:
            processed_5min = {"error": "Failed to fetch 5-minute candlestick data"}

        # 결과 통합
        final_result = {
            "timestamp": current_datetime,  # 처리 시점의 시간 추가
            "current_price": current_price,
            "volume_24h": volume_24h,
            "summary_30d": summary_30d,
            "processed_5min": processed_5min
        }

        # JSON 변환
        json_result = convert_to_json(final_result)
        print("최종 JSON 데이터:")
        print(json_result)

    except Exception as e:
        print(f"오류 발생: {e}")
