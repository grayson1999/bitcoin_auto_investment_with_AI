from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Trade(Base):
    """
    거래 내역을 저장하는 테이블
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)  # Primary Key
    timestamp = Column(DateTime, nullable=False)  # 거래 발생 시각
    action = Column(String(10), nullable=False)  # 거래 유형 ('buy', 'sell', 'hold')
    currency = Column(String(10), nullable=False)  # 거래 자산 (BTC, XRP 등)
    amount = Column(Float, nullable=False)  # 거래 금액/수량
    price = Column(Float, nullable=False)  # 거래 당시 자산 가격
    total_value = Column(Float, nullable=False)  # 거래 총 금액
    reason = Column(String, nullable=True)  # GPT 판단 근거

    def __repr__(self):
        return f"<Trade(id={self.id}, action={self.action}, currency={self.currency}, amount={self.amount})>"


class Performance(Base):
    """
    수익률 및 누적 수익률을 저장하는 테이블
    """
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)  # Primary Key
    timestamp = Column(DateTime, nullable=False)  # 기록 시각
    profit = Column(Float, nullable=False)  # 특정 거래의 수익금
    profit_rate = Column(Float, nullable=False)  # 특정 거래의 수익률 (%)
    cumulative_profit = Column(Float, nullable=False)  # 누적 수익금
    cumulative_profit_rate = Column(Float, nullable=False)  # 누적 수익률 (%)

    def __repr__(self):
        return f"<Performance(id={self.id}, profit={self.profit}, profit_rate={self.profit_rate})>"


class Portfolio(Base):
    """
    현재 포트폴리오 상태를 저장하는 테이블
    """
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)  # Primary Key
    timestamp = Column(DateTime, nullable=False)  # 기록 시각
    cash_balance = Column(Float, nullable=False)  # 현금 잔액
    total_investment = Column(Float, nullable=False)  # 총 투자 금액
    currency = Column(String(10), nullable=False)  # 투자 대상 자산
    target_asset_balance = Column(Float, nullable=False)  # 현재 자산 보유 수량
    avg_buy_price = Column(Float, nullable=False)  # 평균 매수 가격

    def __repr__(self):
        return f"<Portfolio(id={self.id}, currency={self.currency}, cash_balance={self.cash_balance})>"
