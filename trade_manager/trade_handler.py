import pyupbit
import logging
import os
from dotenv import load_dotenv

# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

# .env 파일 로드
load_dotenv()

# .env 파일에서 API 키 로드
load_dotenv()
UPBIT_ACCESS_KEY = os.getenv("UPBIT_API_KEY")
UBPIT_SECRET_KEY = os.getenv("UPBIT_API_SECRET")

# Upbit 객체 초기화
upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UBPIT_SECRET_KEY)


def execute_trade(action: str, amount: float, market: str) -> dict:
    """
    매수 또는 매도 명령을 실행.
    :param action: str - 매매 유형 ('buy' 또는 'sell').
    :param amount: float - 매매할 금액 또는 수량.
    :param market: str - 거래 시장 (예: 'KRW-BTC').
    :return: dict - 거래 결과.
    """
    try:
        if action not in ["buy", "sell"]:
            raise ValueError(f"Invalid action: {action}")

        if action == "buy":
            # 매수 요청 (시장가 매수)
            result = upbit.buy_market_order(market, amount)
        elif action == "sell":
            # 매도 요청 (시장가 매도)
            result = upbit.sell_market_order(market, amount)

        logging.info(f"Trade executed: {action} {amount} in {market}. Result: {result}")
        return result

    except Exception as e:
        logging.error(f"Trade execution failed: {e}")
        return {"error": str(e)}


def log_transaction(action: str, result: dict) -> None:
    """
    거래 내역을 로깅.
    :param action: str - 매매 유형 ('buy' 또는 'sell').
    :param result: dict - 거래 결과 데이터.
    """
    try:
        if "error" in result:
            logging.error(f"Trade failed: {result['error']}")
        else:
            logging.info(
                f"Transaction Log - Action: {action}, Market: {result.get('market')}, "
                f"Volume: {result.get('volume')}, Price: {result.get('price')}, "
                f"UUID: {result.get('uuid')}"
            )
    except Exception as e:
        logging.error(f"Error while logging transaction: {e}")
        
if __name__ == "__main__":
    # 테스트 데이터
    test_action = "buy"
    test_amount = 10000  # 매수 금액 (KRW)
    test_market = "KRW-BTC"  # 비트코인 원화 시장

    # 매매 실행
    trade_result = execute_trade(test_action, test_amount, test_market)

    # 거래 결과 로깅
    log_transaction(test_action, trade_result)
