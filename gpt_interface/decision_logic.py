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

