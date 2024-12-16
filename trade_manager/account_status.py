import logging

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
