import os
from dotenv import load_dotenv
import pyupbit

# 환경 변수 로드
load_dotenv()

# 상수 정의
DAYS_TO_FETCH = 30  # 가져올 데이터의 일수
INTERVAL_OPTION = "day"  # 조회 단위 (일봉, 주봉, 월봉 등)

# 업비트 차트 데이터 가져오기
def fetch_chart_data(days, interval):
    """
    업비트 차트 데이터를 가져옵니다.

    Args:
        days (int): 가져올 데이터의 일수
        interval (str): 조회 단위 (예: "day", "week", "minute1")

    Returns:
        DataFrame: OHLCV 데이터
    """
    return pyupbit.get_ohlcv("KRW-BTC", count=days, interval=interval)

# 실행
if __name__ == "__main__":
    df = fetch_chart_data(DAYS_TO_FETCH, INTERVAL_OPTION)
    print(df.tail())
