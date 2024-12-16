import logging
from typing import Dict

# 판단 로직 모듈


from typing import Dict, Tuple, Optional  # Tuple과 Optional을 포함하여 typing 임포트

def make_decision(gpt_response: Dict, portfolio: Dict) -> Tuple[str, Optional[float]]:
    """
    GPT 응답 데이터를 기반으로 매수/매도/보류 판단을 결정하고 실행 가능성을 확인합니다.
    :param gpt_response: Dict - GPT 응답 데이터.
    :param portfolio: Dict - 현재 포트폴리오 상태 (현금 및 투자 정보).
    :return: Tuple[str, Optional[float]] - 결정된 행동 ('buy', 'sell', 'hold') 및 실행 금액 (None일 수 있음).
    """
    try:
        fee_rate = 0.0005  # 거래 수수료율 0.05%
        action = gpt_response.get("action")
        amount_str = gpt_response.get("amount")
        reason = gpt_response.get("reason", "No reason provided.")

        # 'hold' 처리
        if action == "hold":
            logging.info(f"Decision: {action}. Reason: {reason}")
            return "hold", 0

        # 금액 변환
        try:
            if isinstance(amount_str, (float, int)):
                amount = float(amount_str)
                currency = "BTC" if amount < 1 else "KRW"
            else:
                amount = float(amount_str.split()[0])  # 금액 추출
                currency = amount_str.split()[1]      # 통화 단위 추출 (KRW 또는 BTC)
        except (ValueError, IndexError):
            raise ValueError(f"Invalid amount format in GPT response: {amount_str}")

        # 행동 유효성 확인
        if action not in ["buy", "sell", "hold"]:
            raise ValueError(f"Invalid action received from GPT: {action}")

        logging.info(f"GPT Decision: {action} {amount} {currency}. Reason: {reason}")

        # 구매 로직
        if action == "buy":
            cash_balance = portfolio.get("cash_balance", 0)
            min_purchase_amount = 5000  # 최소 구매 가능 금액 (KRW)

            # 구매 가능 금액 계산
            max_purchase_amount = cash_balance / (1 + fee_rate)
            if max_purchase_amount < min_purchase_amount:
                logging.warning(
                    f"Insufficient cash for buying: Available {cash_balance:.2f} KRW, "
                    f"but minimum purchase amount is {min_purchase_amount} KRW."
                )
                return "hold", 0

            # 요청 금액 조정
            if amount > max_purchase_amount:
                adjusted_amount = max(min_purchase_amount, max_purchase_amount)
                logging.warning(
                    f"Requested amount {amount:.2f} KRW exceeds available balance. Adjusting to {adjusted_amount:.2f} KRW."
                )
                return "buy", adjusted_amount

            logging.info(f"Buy decision: {amount:.2f} KRW approved.")
            return "buy", amount

        # 판매 로직
        elif action == "sell":
            target_asset = portfolio.get("target_asset", {})
            asset_balance = target_asset.get("balance", 0)
            current_price = portfolio.get("current_price", 0)

            if currency == "BTC":
                if amount > asset_balance:
                    logging.warning(
                        f"Insufficient BTC for selling: Required {amount:.8f} BTC, Available {asset_balance:.8f} BTC."
                    )
                    return "hold", 0

                # 체결 금액 및 수익 계산
                total_value = amount * current_price  # 체결 금액
                net_value = total_value * (1 - fee_rate)  # 수익 금액 (수수료 차감 후)
                logging.info(
                    f"Sell decision: {amount:.8f} BTC will be sold for an estimated {net_value:.2f} KRW after fees."
                )
                return "sell", amount

        # 기본값
        return "hold", 0

    except Exception as e:
        logging.error(f"Error in make_decision: {e}")
        return "hold", 0  # 오류 발생 시 기본값 반환





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