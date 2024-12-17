from sqlalchemy.orm import Session
from db.models import Trade, Performance, Portfolio
import datetime
import logging

# ===========================
# Trade 관련 CRUD
# ===========================

def create_trade(db: Session, trade_data: dict):
    """
    거래 기록 생성
    :param db: SQLAlchemy Session
    :param trade_data: 거래 데이터 (dict)
    """
    try:
        trade = Trade(**trade_data)
        db.add(trade)
        db.commit()
        db.refresh(trade)
        logging.info(f"Trade created: {trade}")
        return trade
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create trade: {e}")
        raise


def get_trades(db: Session, limit: int = 100):
    """
    모든 거래 기록 조회
    :param db: SQLAlchemy Session
    :param limit: 조회할 최대 거래 수
    """
    return db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()


def get_trade_by_id(db: Session, trade_id: int):
    """
    특정 거래 기록 조회
    :param db: SQLAlchemy Session
    :param trade_id: 거래 ID
    """
    return db.query(Trade).filter(Trade.id == trade_id).first()


def delete_trade(db: Session, trade_id: int):
    """
    거래 기록 삭제
    :param db: SQLAlchemy Session
    :param trade_id: 거래 ID
    """
    trade = get_trade_by_id(db, trade_id)
    if trade:
        db.delete(trade)
        db.commit()
        logging.info(f"Trade deleted: {trade}")
        return True
    return False


# ===========================
# Performance 관련 CRUD
# ===========================

def create_performance(db: Session, performance_data: dict):
    """
    수익률 기록 생성
    :param db: SQLAlchemy Session
    :param performance_data: 수익률 데이터 (dict)
    """
    try:
        performance = Performance(**performance_data)
        db.add(performance)
        db.commit()
        db.refresh(performance)
        logging.info(f"Performance created: {performance}")
        return performance
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create performance: {e}")
        raise


def get_performance_records(db: Session, limit: int = 100):
    """
    모든 수익률 기록 조회
    :param db: SQLAlchemy Session
    :param limit: 조회할 최대 기록 수
    """
    return db.query(Performance).order_by(Performance.timestamp.desc()).limit(limit).all()


def get_latest_performance(db: Session):
    """
    가장 최근 수익률 기록 조회
    :param db: SQLAlchemy Session
    """
    return db.query(Performance).order_by(Performance.timestamp.desc()).first()


def calculate_cumulative_profit_and_rate(db: Session) -> dict:
    """
    Performance 테이블에서 누적 수익과 누적 수익률을 계산합니다.
    :param db: SQLAlchemy Session
    :return: dict - 누적 수익과 누적 수익률
    """
    try:
        # 가장 최근 누적 데이터를 가져옴
        latest_performance = db.query(Performance).order_by(Performance.timestamp.desc()).first()

        if latest_performance:
            return {
                "cumulative_profit_loss": latest_performance.cumulative_profit,
                "cumulative_profit_rate": latest_performance.cumulative_profit_rate,
            }
        else:
            # 데이터가 없는 경우 기본값 반환
            return {
                "cumulative_profit_loss": 0.0,
                "cumulative_profit_rate": 0.0,
            }

    except Exception as e:
        logging.error(f"Error calculating cumulative performance: {e}")
        return {
            "cumulative_profit_loss": 0.0,
            "cumulative_profit_rate": 0.0,
        }


# ===========================
# Portfolio 관련 CRUD
# ===========================

def update_portfolio(db: Session, portfolio_data: dict):
    """
    포트폴리오 상태 갱신
    :param db: SQLAlchemy Session
    :param portfolio_data: 포트폴리오 데이터 (dict)
    """
    try:
        portfolio = db.query(Portfolio).order_by(Portfolio.timestamp.desc()).first()
        if portfolio:
            for key, value in portfolio_data.items():
                setattr(portfolio, key, value)
            portfolio.timestamp = datetime.datetime.now()
        else:
            portfolio = Portfolio(**portfolio_data)
            db.add(portfolio)

        db.commit()
        db.refresh(portfolio)
        logging.info(f"Portfolio updated: {portfolio}")
        return portfolio
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to update portfolio: {e}")
        raise


def get_portfolio(db: Session):
    """
    현재 포트폴리오 상태 조회
    :param db: SQLAlchemy Session
    """
    return db.query(Portfolio).order_by(Portfolio.timestamp.desc()).first()
