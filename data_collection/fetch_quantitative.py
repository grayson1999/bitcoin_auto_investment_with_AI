# data_collection/fetch_quantitative.py
import pandas as pd
from pyupbit import get_ohlcv, get_current_price

# 업비트 API를 활용한 데이터 수집 모듈

def fetch_current_price(market: str = "KRW-BTC") -> float:
    """
    주어진 암호화폐 시장의 현재 가격을 가져옵니다.
    :param market: str - 시장 식별자, 기본값은 KRW-BTC.
    :return: float - 현재 거래 가격 또는 실패 시 None.
    """
    try:
        price = get_current_price(market)
        return price
    except Exception as e:
        print(f"현재 가격 데이터를 가져오는 중 오류 발생: {e}")
        return None

def fetch_24h_volume(market: str = "KRW-BTC") -> float:
    """
    주어진 암호화폐 시장의 24시간 거래량을 가져옵니다.
    :param market: str - 시장 식별자, 기본값은 KRW-BTC.
    :return: float - 24시간 거래량 또는 실패 시 None.
    """
    try:
        data = get_ohlcv(market, interval="day", count=1)
        volume = data.iloc[-1]["volume"]
        return volume
    except Exception as e:
        print(f"24시간 거래량 데이터를 가져오는 중 오류 발생: {e}")
        return None

def fetch_30d_candlestick(market: str = "KRW-BTC", count: int = 30) -> pd.DataFrame:
    """
    주어진 암호화폐 시장의 최근 30일 일봉 데이터를 가져옵니다.
    :param market: str - 시장 식별자, 기본값은 KRW-BTC.
    :param count: int - 가져올 일봉 데이터 개수, 기본값은 30.
    :return: DataFrame - 일봉 데이터 또는 실패 시 None.
    """
    try:
        data = get_ohlcv(market, interval="day", count=count)
        return data
    except Exception as e:
        print(f"30일 일봉 데이터를 가져오는 중 오류 발생: {e}")
        return None
    
def fetch_5min_data(market: str = "KRW-BTC", count: int = 36) -> pd.DataFrame:
    """
    지정된 암호화폐 시장의 5분 봉 데이터를 가져옵니다.
    :param market: str - 시장 식별자, 기본값은 KRW-BTC.
    :param count: int - 가져올 봉 데이터의 개수, 기본값은 36개 (3시간).
    :return: DataFrame - 5분 봉 데이터 또는 None.
    """
    try:
        data = get_ohlcv(market, interval="minute5", count=count)
        return data
    except Exception as e:
        print(f"5분 봉 데이터를 가져오는 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # 현재 가격 확인
    current_price = fetch_current_price()
    print(f"현재 비트코인 가격: {current_price}")

    # 24시간 거래량 확인
    volume_24h = fetch_24h_volume()
    print(f"24시간 거래량: {volume_24h}")

    # 30일 일봉 데이터 확인
    candlestick_30d = fetch_30d_candlestick()
    if candlestick_30d is not None:
        print("최근 30일 일봉 데이터:")
        print(candlestick_30d.head())

    # 5분 봉 데이터 확인
    raw_5min_data = fetch_5min_data()
    if raw_5min_data is not None:
        print("최근 3시간 5분 봉 데이터:")
        print(raw_5min_data.head())
