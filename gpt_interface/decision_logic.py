import logging
from typing import Dict

# 판단 로직 모듈


def make_decision(gpt_response: Dict, portfolio: Dict) -> str:
    """
    GPT 응답 데이터를 기반으로 매수/매도/보류 판단을 결정합니다.
    :param gpt_response: Dict - GPT 응답 데이터.
    :param portfolio: Dict - 현재 포트폴리오 상태 (현금 및 투자 정보).
    :return: str - 결정된 행동 ('buy', 'sell', 'hold').
    """
    try:
        action = gpt_response.get("action")
        amount = gpt_response.get("amount")

        if action not in ["buy", "sell", "hold"]:
            raise ValueError(f"Invalid action received from GPT: {action}")

        logging.info(f"GPT Decision: {action} with amount: {amount}")
        return action

    except Exception as e:
        logging.error(f"Error in make_decision: {e}")
        return "hold"  # 오류 발생 시 기본값으로 '보류'


def evaluate_decision(previous_decisions: list, market_data: Dict) -> None:
    """
    이전 판단 결과를 기반으로 판단 로직의 성과를 평가합니다.
    :param previous_decisions: list - 이전 판단 기록.
    :param market_data: Dict - 시장 데이터 (현재 가격, 변동성 등).
    :return: None
    """
    try:
        # 간단한 평가: 이전 결정과 시장 데이터를 비교하여 수익 여부 분석
        profit_count = sum(
            1 for decision in previous_decisions if decision.get("profit") > 0
        )
        loss_count = len(previous_decisions) - profit_count

        logging.info(
            f"Evaluation - Profitable decisions: {profit_count}, Loss decisions: {loss_count}"
        )

    except Exception as e:
        logging.error(f"Error in evaluate_decision: {e}")


def calculate_performance(previous_transactions: list) -> float:
    """
    이전 거래 데이터를 기반으로 수익률을 계산합니다.
    :param previous_transactions: list - 이전 거래 내역 (매수/매도 가격, 수량 포함).
    :return: float - 총 수익률 (%).
    """
    try:
        initial_balance = sum(
            tx.get("initial_value", 0) for tx in previous_transactions
        )
        final_balance = sum(tx.get("final_value", 0) for tx in previous_transactions)

        if initial_balance == 0:
            raise ValueError("Initial balance cannot be zero for performance calculation.")

        performance = ((final_balance - initial_balance) / initial_balance) * 100
        logging.info(f"Total Performance: {performance:.2f}%")
        return performance

    except Exception as e:
        logging.error(f"Error in calculate_performance: {e}")
        return 0.0

if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # 예시 데이터: GPT 응답 데이터
    gpt_response = {
        "action": "buy",
        "amount": "0.0035",
        "reason": (
            "The current price shows an upward trend and is above the recent average, "
            "providing a good opportunity to increase your Bitcoin holdings. "
            "With sufficient cash available, it is advisable to reinvest the full amount "
            "of your Bitcoin to capitalize on potential future gains."
        ),
    }

    # 예시 데이터: 현재 포트폴리오 상태
    portfolio = {
        "cash_balance": 1000000.0,  # 100만 원
        "invested_assets": [
            {"currency": "BTC", "balance": 0.005, "avg_buy_price": 45000000.0}  # 0.005 BTC 보유
        ],
    }

    # 1. GPT 응답 데이터를 토대로 행동 결정
    action = make_decision(gpt_response, portfolio)
    logging.info(f"결정된 행동: {action}")

    # 2. 이전 판단 결과 평가
    previous_decisions = [
        {"action": "buy", "profit": 10000.0},
        {"action": "sell", "profit": -5000.0},
        {"action": "hold", "profit": 0.0},
    ]
    evaluate_decision(previous_decisions, market_data={"current_price": 46000000.0})

    # 3. 수익률 계산
    previous_transactions = [
        {"initial_value": 1000000.0, "final_value": 1050000.0},  # 수익 5%
        {"initial_value": 500000.0, "final_value": 450000.0},    # 손실 10%
    ]
    total_performance = calculate_performance(previous_transactions)
    logging.info(f"총 수익률: {total_performance:.2f}%")