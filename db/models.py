from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# 투자 요약 테이블
class InvestmentSummary(Base):
    __tablename__ = "investment_summary"
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    total_investment = Column(Float, nullable=False, default=0.0)
    total_profit_loss = Column(Float, nullable=False, default=0.0)
    profit_rate = Column(Float, nullable=False, default=0.0)
    total_trades = Column(Integer, nullable=False, default=0)
    cumulative_profit_loss = Column(Float, nullable=False, default=0.0)  # 누적 수익 금액
    cumulative_profit_rate = Column(Float, nullable=False, default=0.0)  # 누적 수익률


# 거래 내역 테이블
class TradeLogs(Base):
    __tablename__ = "trade_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)  # 'buy', 'sell'
    amount = Column(Float, nullable=False)  # 거래 금액
    price = Column(Float, nullable=False)  # 거래 단가
    total_value = Column(Float, nullable=False)  # 거래 총 금액
    currency = Column(String, nullable=False)  # 암호화폐 종류
    reason = Column(String, nullable=True)  # GPT에서 제공한 이유
    timestamp = Column(DateTime, nullable=False)

# 포트폴리오 테이블
class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, nullable=False)  # 암호화폐 종류
    balance = Column(Float, nullable=False, default=0.0)
    avg_buy_price = Column(Float, nullable=False, default=0.0)
    total_investment = Column(Float, nullable=False, default=0.0)

# GPT 로그 테이블
class GptLogs(Base):
    __tablename__ = "gpt_logs"
    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(String, nullable=False)
    action = Column(String, nullable=False)  # 'buy', 'sell', 'hold'
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)  # GPT 제공 이유
    timestamp = Column(DateTime, nullable=False)
