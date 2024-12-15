# data_collection/fetch_quantitative.py
import pandas as pd
from pyupbit import get_ohlcv, get_current_price
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests

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
    지정된 암호화폐 시장의 5분 봉 데이터를 가져옵니다 (3시간).
    :param market: str - 시장 식별자, 기본값은 KRW-BTC.
    :param count: int - 가져올 봉 데이터의 개수, 기본값은 36개 (3시간).
    :return: DataFrame - 5분 봉 데이터 또는 None.
    """
    try:
        # 업비트 API 호출로 5분 봉 데이터 가져오기
        data = get_ohlcv(market, interval="minute5", count=count)
        return data
    except Exception as e:
        print(f"5분 봉 데이터를 가져오는 중 오류 발생: {e}")
        return None


def fetch_portfolio_status(access_key: str, secret_key: str) -> dict:
    """
    업비트 계정의 보유 자산 및 투자 상태를 가져옵니다.
    :param access_key: str - 업비트 API Access Key.
    :param secret_key: str - 업비트 API Secret Key.
    :return: dict - 보유 자산 및 투자 상태 정보.
    """
    try:
        # JWT 토큰 생성
        payload = {
            "access_key": access_key,
            "nonce": str(uuid.uuid4())
        }
        jwt_token = jwt.encode(payload, secret_key)
        authorization_token = f"Bearer {jwt_token}"

        headers = {"Authorization": authorization_token}

        # API 요청
        response = requests.get("https://api.upbit.com/v1/accounts", headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.json()}")
            return {"error": f"Failed to fetch portfolio status. Status code: {response.status_code}"}

        # 응답 데이터를 파싱하여 포트폴리오 상태 구성
        assets = response.json()
        portfolio = {
            "cash_balance": 0.0,
            "invested_assets": [],
            "total_investment": 0.0  # 누적 투자 금액
        }

        for asset in assets:
            if asset["currency"] == "KRW":
                # 현금 잔고
                portfolio["cash_balance"] = float(asset["balance"])
            else:
                # 투자 자산
                balance = float(asset["balance"])
                avg_buy_price = float(asset.get("avg_buy_price", 0))
                total_asset_investment = balance * avg_buy_price  # 해당 자산의 투자 금액

                invested_asset = {
                    "currency": asset["currency"],
                    "balance": balance,
                    "avg_buy_price": avg_buy_price,
                    "total_investment": round(total_asset_investment, 2)  # 개별 자산 누적 투자 금액
                }
                portfolio["invested_assets"].append(invested_asset)

                # 총 누적 투자 금액 업데이트
                portfolio["total_investment"] += total_asset_investment

        portfolio["total_investment"] = round(portfolio["total_investment"], 2)  # 소수점 처리
        return portfolio

    except Exception as e:
        print(f"포트폴리오 상태 조회 중 오류 발생: {e}")
        return {"error": f"An error occurred while fetching portfolio status: {e}"}

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
        
    import os
    from dotenv import load_dotenv
    
    # 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(BASE_DIR, ".env")

    # .env 파일 로드
    load_dotenv()

    # .env 파일에서 API 키 로드
    load_dotenv()
    ACCESS_KEY = os.getenv("UPBIT_API_KEY")
    SECRET_KEY = os.getenv("UPBIT_API_SECRET")

    # 포트폴리오 상태 조회
    portfolio_status = fetch_portfolio_status(ACCESS_KEY, SECRET_KEY)

    # 결과 출력
    print("포트폴리오 상태:")
    print(portfolio_status)
