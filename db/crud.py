from sqlalchemy.orm import Session
from db.models import InvestmentSummary, TradeLogs, Portfolio, GptLogs

# 투자 요약 데이터 생성 함수
def create_investment_summary(db: Session, summary_data: dict):
    """
    투자 요약 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param summary_data: dict - 투자 요약 데이터
    :return: InvestmentSummary 객체
    """
    # InvestmentSummary 모델 인스턴스 생성
    summary = InvestmentSummary(**summary_data)
    # 데이터베이스에 추가 및 커밋
    db.add(summary)
    db.commit()
    # 생성된 데이터 새로고침 후 반환
    db.refresh(summary)
    return summary

# 거래 로그 데이터 생성 함수
def create_trade_log(db: Session, trade_data: dict):
    """
    거래 로그 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param trade_data: dict - 거래 로그 데이터
    :return: TradeLogs 객체
    """
    # TradeLogs 모델 인스턴스 생성
    trade_log = TradeLogs(**trade_data)
    # 데이터베이스에 추가 및 커밋
    db.add(trade_log)
    db.commit()
    # 생성된 데이터 새로고침 후 반환
    db.refresh(trade_log)
    return trade_log

# 포트폴리오 데이터 생성 함수
def create_portfolio(db: Session, portfolio_data: dict):
    """
    포트폴리오 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param portfolio_data: dict - 포트폴리오 데이터
    :return: Portfolio 객체
    """
    # Portfolio 모델 인스턴스 생성
    portfolio = Portfolio(**portfolio_data)
    # 데이터베이스에 추가 및 커밋
    db.add(portfolio)
    db.commit()
    # 생성된 데이터 새로고침 후 반환
    db.refresh(portfolio)
    return portfolio

# GPT 로그 데이터 생성 함수
def create_gpt_log(db: Session, gpt_data: dict):
    """
    GPT 로그 데이터를 데이터베이스에 추가합니다.
    :param db: SQLAlchemy 세션 객체
    :param gpt_data: dict - GPT 로그 데이터
    :return: GptLogs 객체
    """
    # GptLogs 모델 인스턴스 생성
    gpt_log = GptLogs(**gpt_data)
    # 데이터베이스에 추가 및 커밋
    db.add(gpt_log)
    db.commit()
    # 생성된 데이터 새로고침 후 반환
    db.refresh(gpt_log)
    return gpt_log
