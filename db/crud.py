from sqlalchemy.orm import Session
from db.models import InvestmentSummary, TradeLogs, Portfolio, GptLogs
import datetime
import logging

# 투자 요약 데이터를 생성하는 함수
def create_investment_summary(db: Session, summary_data: dict) -> InvestmentSummary:
    """
    투자 요약 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param summary_data: dict - 투자 요약 데이터
    :return: InvestmentSummary 객체
    """
    summary = InvestmentSummary(**summary_data)  # InvestmentSummary 인스턴스 생성
    db.add(summary)  # 데이터베이스에 추가
    db.commit()  # 변경 사항 커밋
    db.refresh(summary)  # 새로 생성된 데이터 새로고침
    return summary  # 생성된 데이터 반환

# 거래 로그 데이터를 생성하는 함수
def create_trade_log(db: Session, trade_data: dict) -> TradeLogs:
    """
    거래 로그 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param trade_data: dict - 거래 로그 데이터
    :return: TradeLogs 객체
    """
    trade_log = TradeLogs(**trade_data)  # TradeLogs 인스턴스 생성
    db.add(trade_log)  # 데이터베이스에 추가
    db.commit()  # 변경 사항 커밋
    db.refresh(trade_log)  # 새로 생성된 데이터 새로고침
    return trade_log  # 생성된 데이터 반환

# 포트폴리오 데이터를 생성하는 함수
def create_portfolio(db: Session, portfolio_data: dict) -> Portfolio:
    """
    포트폴리오 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param portfolio_data: dict - 포트폴리오 데이터
    :return: Portfolio 객체
    """
    portfolio = Portfolio(**portfolio_data)  # Portfolio 인스턴스 생성
    db.add(portfolio)  # 데이터베이스에 추가
    db.commit()  # 변경 사항 커밋
    db.refresh(portfolio)  # 새로 생성된 데이터 새로고침
    return portfolio  # 생성된 데이터 반환

# GPT 로그 데이터를 생성하는 함수
def create_gpt_log(db: Session, gpt_data: dict) -> GptLogs:
    """
    GPT 로그 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param gpt_data: dict - GPT 로그 데이터
    :return: GptLogs 객체
    """
    gpt_log = GptLogs(**gpt_data)  # GptLogs 인스턴스 생성
    db.add(gpt_log)  # 데이터베이스에 추가
    db.commit()  # 변경 사항 커밋
    db.refresh(gpt_log)  # 새로 생성된 데이터 새로고침
    return gpt_log  # 생성된 데이터 반환

# 누적 수익 데이터를 업데이트하는 함수
def update_cumulative_summary(db: Session, new_profit_loss: float, new_profit_rate: float):
    summary = db.query(InvestmentSummary).order_by(InvestmentSummary.id.desc()).first()
    if summary:
        summary.cumulative_profit_loss += new_profit_loss
        total_trades = summary.total_trades + 1
        summary.cumulative_profit_rate = (
            (summary.cumulative_profit_rate * summary.total_trades + new_profit_rate) / total_trades
        )
        summary.total_trades = total_trades
        db.commit()
        db.refresh(summary)  # 명시적으로 새로고침
    else:
        summary = InvestmentSummary(
            start_date=datetime.datetime.now(),
            end_date=None,
            cumulative_profit_loss=new_profit_loss,
            cumulative_profit_rate=new_profit_rate,
            total_trades=1,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)  # 새로 생성된 객체도 새로고침
        print(f"Created New Summary: {summary.cumulative_profit_loss}, {summary.cumulative_profit_rate}")
    return summary




# 누적 수익 데이터를 조회하는 함수
def get_cumulative_summary(db: Session) -> InvestmentSummary:
    summary = db.query(InvestmentSummary).order_by(InvestmentSummary.id.desc()).first()
    if not summary:
        logging.warning("Cumulative summary not found, initializing default values.")
        summary = InvestmentSummary(
            start_date=datetime.datetime.now(),
            end_date=None,
            cumulative_profit_loss=0.0,
            cumulative_profit_rate=0.0,
            total_trades=0,
        )
        db.add(summary)
        db.commit()
        db.refresh(summary)
    return summary


# 최근 거래 로그를 조회하는 함수
def get_last_trade_log(db: Session) -> TradeLogs:
    """
    가장 최근 거래 로그를 가져옵니다.
    :param db: SQLAlchemy 세션 객체
    :return: TradeLogs 객체 또는 None
    """
    return db.query(TradeLogs).order_by(TradeLogs.timestamp.desc()).first()  # 최신 거래 로그 반환

def calculate_cumulative_profit_and_rate(db: Session):
    """
    거래 로그를 기반으로 누적 수익 금액과 누적 수익률을 계산합니다.
    :param db: SQLAlchemy 세션 객체
    :return: dict - 누적 수익 금액과 누적 수익률
    """
    trade_logs = db.query(TradeLogs).order_by(TradeLogs.timestamp).all()
    
    if not trade_logs:
        return {"cumulative_profit_loss": 0.0, "cumulative_profit_rate": 0.0}
    
    total_investment = 0.0  # 총 투자 금액
    cumulative_profit_loss = 0.0  # 누적 수익 금액
    total_balance = 0.0  # 현재까지 보유 수량

    for log in trade_logs:
        if log.action == "buy":
            # 매수 시 투자 금액 증가
            total_investment += log.total_value
            total_balance += log.amount
        elif log.action == "sell":
            # 매도 시 손익 계산
            profit = (log.price * log.amount) - (total_investment * (log.amount / total_balance))
            cumulative_profit_loss += profit
            total_investment -= total_investment * (log.amount / total_balance)  # 투자 금액에서 매도된 부분 차감
            total_balance -= log.amount

    # 누적 수익률 계산
    cumulative_profit_rate = (cumulative_profit_loss / total_investment * 100) if total_investment > 0 else 0.0

    return {
        "cumulative_profit_loss": round(cumulative_profit_loss, 2),
        "cumulative_profit_rate": round(cumulative_profit_rate, 2),
    }