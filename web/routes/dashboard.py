from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import InvestmentSummary, Portfolio, TradeLogs
from datetime import datetime

router = APIRouter()

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="web/templates")
def format_reason(reason: str) -> str:
    """
    긴 이유 텍스트를 '. (마침표)' 기준으로 줄바꿈 처리.
    """
    if reason:
        return reason.replace('. ', '.\n')
    return "N/A"

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # 투자 요약 정보 가져오기
    investment_summary = db.query(InvestmentSummary).first()

    # 포트폴리오 데이터 변환
    portfolio = [
        {"currency": asset.currency, "balance": asset.balance, "avg_buy_price": asset.avg_buy_price}
        for asset in db.query(Portfolio).all()
    ]

    # 최근 거래 기록 가져오기
    recent_trades = [
        {
            "timestamp": trade.timestamp.strftime('%Y-%m-%d %H:%M:%S') if isinstance(trade.timestamp, datetime) else str(trade.timestamp),
            "action": trade.action,
            "amount": f"{trade.amount:.8f} BTC" if trade.amount <= 1 else f"{int(trade.amount):,} KRW",  # 통화 처리
            "reason": format_reason(trade.reason),  # 이유 줄바꿈 처리
        }
        for trade in db.query(TradeLogs).order_by(TradeLogs.timestamp.desc()).limit(5).all()
    ]

    # 템플릿에 데이터 전달
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": {
                "current_profit_rate": investment_summary.profit_rate,
                "current_profit_loss": investment_summary.total_profit_loss,
                "cumulative_profit_rate": investment_summary.cumulative_profit_rate,
                "cumulative_profit_loss": investment_summary.cumulative_profit_loss,
                "portfolio": portfolio,
                "recent_trades": recent_trades,
            },
        },
    )


@router.get("/trade-logs")
def get_trade_logs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    """
    거래 기록 API 엔드포인트.
    페이지 및 항목 수를 기반으로 거래 기록 반환.
    """
    total_records = db.query(TradeLogs).count()
    trade_logs = (
        db.query(TradeLogs)
        .order_by(TradeLogs.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # 거래 기록 변환
    formatted_trades = [
        {
            "timestamp": trade.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # 날짜 포맷팅
            "action": trade.action,
            "amount": f"{trade.amount:.8f} BTC" if trade.amount <= 1 else f"{int(trade.amount):,} KRW",  # 통화 처리
            "reason": format_reason(trade.reason),  # 이유 줄바꿈 처리
        }
        for trade in trade_logs
    ]

    return {
        "total_records": total_records,
        "page": page,
        "per_page": per_page,
        "trade_logs": formatted_trades,
    }



@router.get("/performance-graph")
def get_performance_graph(db: Session = Depends(get_db)):
    """
    성과 그래프 데이터 API.
    - 누적 수익률 변화 (날짜별 누적 수익률)
    - 일간 손익 추세
    """
    # 날짜별 누적 수익률 가져오기
    investment_data = (
        db.query(InvestmentSummary.start_date, InvestmentSummary.cumulative_profit_rate)
        .order_by(InvestmentSummary.start_date.asc())
        .all()
    )

    # 날짜별 일간 손익 가져오기
    daily_profit_data = (
        db.query(InvestmentSummary.start_date, InvestmentSummary.total_profit_loss)
        .order_by(InvestmentSummary.start_date.asc())
        .all()
    )

    # 데이터 변환
    cumulative_profit_rate = [
        {"date": record[0].strftime("%Y-%m-%d"), "rate": record[1]} for record in investment_data
    ]
    daily_profit_loss = [
        {"date": record[0].strftime("%Y-%m-%d"), "loss": record[1]} for record in daily_profit_data
    ]

    # 응답 데이터 반환
    return {
        "cumulative_profit_rate": cumulative_profit_rate,
        "daily_profit_loss": daily_profit_loss,
    }