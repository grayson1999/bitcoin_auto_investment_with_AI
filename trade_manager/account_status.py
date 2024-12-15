import logging

def calculate_profit_loss(portfolio: dict, current_price: float) -> dict:
    """
    현재 수익률과 손익을 계산합니다.
    :param portfolio: dict - 포트폴리오 데이터 (filtered_portfolio).
    :param current_price: float - 현재 시장 가격.
    :return: dict - 수익률 및 평가 금액 정보.
    """
    try:
        # 포트폴리오에서 대상 자산 데이터 추출
        target_asset = portfolio.get("target_asset")
        if not target_asset:
            raise ValueError("No target asset found in portfolio")

        avg_buy_price = target_asset.get("avg_buy_price", 0)
        balance = target_asset.get("balance", 0)

        # 초기 투자 금액과 현재 평가 금액 계산
        initial_investment = avg_buy_price * balance
        current_valuation = current_price * balance

        # 수익률 계산
        profit_loss = current_valuation - initial_investment
        profit_rate = (profit_loss / initial_investment * 100) if initial_investment > 0 else 0

        # 결과 반환
        return {
            "initial_investment": round(initial_investment, 2),
            "current_valuation": round(current_valuation, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_rate": round(profit_rate, 2),
        }

    except Exception as e:
        logging.error(f"Error calculating profit/loss: {e}")
        return {"error": str(e)}
