import logging
import os
from dotenv import load_dotenv
import requests
import jwt
import uuid
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

def calculate_profit_loss(portfolio: dict, current_price: float) -> dict:
    """
    현재 수익률과 손익을 계산합니다. 중간 매수/매도에 대한 누적 투자 금액을 반영.
    :param portfolio: dict - 포트폴리오 데이터 (filtered_portfolio).
    :param current_price: float - 현재 시장 가격.
    :return: dict - 수익률 및 평가 금액 정보.
    """
    try:
        # 포트폴리오에서 대상 자산 데이터 추출
        target_asset = portfolio.get("target_asset", {})
        if not target_asset:
            raise ValueError("No target asset found in portfolio")

        # 데이터 추출 및 기본값 설정
        avg_buy_price = target_asset.get("avg_buy_price", 0.0)
        balance = target_asset.get("balance", 0.0)
        total_investment = target_asset.get("total_investment", 0.0)

        # 현재 평가 금액 계산
        current_valuation = current_price * balance

        # 수익률 계산
        profit_loss = current_valuation - total_investment
        profit_rate = (profit_loss / total_investment * 100) if total_investment > 0 else 0.0

        # 결과 반환
        return {
            "total_investment": round(total_investment, 2),
            "current_valuation": round(current_valuation, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_rate": round(profit_rate, 2),
        }

    except ZeroDivisionError:
        logging.error("Division by zero in profit/loss calculation")
        return {"error": "Division by zero in calculation"}
    except Exception as e:
        logging.error(f"Error calculating profit/loss: {e}")
        return {"error": str(e)}

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

def filter_bitcoin_portfolio(portfolio: dict, target_currency: str = "BTC") -> dict:
    """
    포트폴리오에서 특정 코인의 정보만 필터링합니다.
    :param portfolio: dict - 전체 포트폴리오 상태.
    :param target_currency: str - 대상 코인 (기본값은 'BTC').
    :return: dict - 현금 잔고와 대상 코인 정보만 포함된 포트폴리오.
    """
    try:
        filtered_portfolio = {"cash_balance": portfolio["cash_balance"],"total_investment": portfolio["total_investment"], "target_asset": {"currency": target_currency, "balance": 0.0, "avg_buy_price": 0.0,}}

        for asset in portfolio["invested_assets"]:
            if asset["currency"] == target_currency:
                filtered_portfolio["target_asset"] = asset
                break

        return filtered_portfolio
    except Exception as e:
        print(f"포트폴리오 필터링 중 오류 발생: {e}")
        return {"error": f"An error occurred while filtering the portfolio: {e}"}


# 포트폴리오 상태 조회
def get_portfolio_status(market_name="KRW-BTC"):
    UPBIT_ACCESS_KEY = os.getenv("UPBIT_API_KEY")
    UPBIT_SECRET_KEY = os.getenv("UPBIT_API_SECRET")
    portfolio_status = fetch_portfolio_status(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    
    ##market 이름 포멧팅
    target_market = market_name.split("-")[1]
    return filter_bitcoin_portfolio(portfolio_status,target_currency=target_market)