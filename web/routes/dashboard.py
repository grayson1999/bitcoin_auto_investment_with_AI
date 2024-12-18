from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Trade, Performance, Portfolio
from datetime import datetime, timedelta
from fastapi.staticfiles import StaticFiles

# FastAPI 앱 초기화
app = FastAPI()

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="web/templates")



app.mount("/static", StaticFiles(directory="web/static"), name="static")

# APIRouter 객체 생성
router = APIRouter()

# 라우터 등록
app.include_router(router, prefix="/api")

# DB 세션 관리
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# **1. 대시보드 데이터 API**
from datetime import datetime, timedelta

@router.get("/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """
    대시보드 데이터를 JSON 형식으로 반환
    """
    # 최근 포트폴리오 데이터
    portfolio = db.query(Portfolio).order_by(Portfolio.timestamp.desc()).first()
    portfolio_data = {
        "currency": portfolio.currency,
        "balance": portfolio.target_asset_balance,
        "total_investment": portfolio.total_investment,
        "cash_balance": portfolio.cash_balance,
        "avg_buy_price": portfolio.avg_buy_price,
    } if portfolio else {}

    # 최근 거래 기록
    recent_trades = db.query(Trade).order_by(Trade.timestamp.desc()).limit(10).all()
    trades_data = [
        {
            "timestamp": trade.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "action": trade.action,
            "currency": trade.currency,
            "amount": trade.amount,
            "price": trade.price,
            "total_value": trade.total_value,
            "reason": trade.reason,
        }
        for trade in recent_trades
    ]

    # 최근 성과 데이터
    latest_performance = db.query(Performance).order_by(Performance.timestamp.desc()).first()
    performance_data = {
        "current_profit_rate": latest_performance.profit_rate if latest_performance else 0,
        "current_profit_loss": latest_performance.profit if latest_performance else 0,
        "cumulative_profit_rate": latest_performance.cumulative_profit_rate if latest_performance else 0,
        "cumulative_profit_loss": latest_performance.cumulative_profit if latest_performance else 0,
    }

    # 12시간 누적 수익 그래프 데이터
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    cumulative_profit_data = db.query(Performance).filter(Performance.timestamp >= twelve_hours_ago).all()
    cumulative_profit_graph = [
        {"date": record.timestamp.strftime("%H:%M"), "value": record.cumulative_profit}
        for record in cumulative_profit_data
    ]

    # 10일간 일일 수익 그래프 데이터
    ten_days_ago = datetime.now() - timedelta(days=10)
    daily_profit_data = db.query(Performance).filter(Performance.timestamp >= ten_days_ago).all()
    daily_profit_graph = [
        {"date": record.timestamp.strftime("%Y-%m-%d"), "value": record.profit}
        for record in daily_profit_data
    ]

    return {
        "portfolio": portfolio_data,
        "recent_trades": trades_data,
        "performance": performance_data,
        "graphs": {
            "cumulative_profit": cumulative_profit_graph,
            "daily_profit": daily_profit_graph,
        },
    }

# **2. 대시보드 템플릿 렌더링**
@router.get("/index", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    대시보드 템플릿 렌더링
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/trades")
async def get_trade_logs(page: int = 1, per_page: int = 5, db: Session = Depends(get_db)):
    """
    거래 기록 반환 (페이지네이션 포함)
    """
    try:
        # 페이지네이션 처리
        offset = (page - 1) * per_page
        total_records = db.query(Trade).count()
        trade_logs = db.query(Trade).order_by(Trade.timestamp.desc()).offset(offset).limit(per_page).all()

        # 직렬화하여 JSON 데이터 반환
        return {
            "trade_logs": [
                {
                    "timestamp": trade.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "action": trade.action,
                    "currency": trade.currency,
                    "amount": trade.amount,
                    "price": trade.price,
                    "total_value": trade.total_value,
                    "reason": trade.reason,
                }
                for trade in trade_logs  # trade는 SQLAlchemy 객체여야 함
            ],
            "page": page,
            "total_records": total_records,
        }
    except Exception as e:
        return {"error": f"Failed to fetch trade logs: {e}"}
