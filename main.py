import schedule
import time
import os
import datetime
import pytz
from dotenv import load_dotenv
from data_collection.fetch_quantitative import *
from data_collection.preprocess import *
from gpt_interface.data_formatter import *
from gpt_interface.request_handler import *
from gpt_interface.decision_logic import *
from trade_manager.trade_handler import *
from trade_manager.account_status import *
from db.database import SessionLocal, init_db
from db.crud import *
from notifications.slack_notifier import SlackNotifier
from deep_translator import GoogleTranslator

# 환경 초기화
def initialize_env():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(BASE_DIR, ".env")
    load_dotenv(dotenv_path)

# 현재 시간 가져오기
def get_current_time():
    seoul_tz = pytz.timezone("Asia/Seoul")
    return datetime.datetime.now(seoul_tz).isoformat()

# 데이터 수집
def collect_market_data():
    current_price = fetch_current_price()  # 현재 비트코인 가격
    volume_24h = fetch_24h_volume()  # 24시간 거래량

    candlestick_30d = fetch_30d_candlestick()
    if candlestick_30d is not None:
        cleaned_30d = handle_missing_values(candlestick_30d)
        normalized_30d = normalize_data(cleaned_30d)
        summary_30d = extract_relevant_data(normalized_30d)
    else:
        summary_30d = {"error": "Failed to fetch 30-day candlestick data"}

    raw_5min_data = fetch_5min_data()
    if raw_5min_data is not None:
        cleaned_5min = handle_missing_values(raw_5min_data)
        processed_5min = preprocess_5min_data(cleaned_5min)
    else:
        processed_5min = {"error": "Failed to fetch 5-minute candlestick data"}

    return {
        "current_price": current_price,
        "volume_24h": volume_24h,
        "summary_30d": summary_30d,
        "processed_5min": processed_5min,
    }

# 포트폴리오 상태 조회
def get_portfolio_status():
    UPBIT_ACCESS_KEY = os.getenv("UPBIT_API_KEY")
    UPBIT_SECRET_KEY = os.getenv("UPBIT_API_SECRET")
    portfolio_status = fetch_portfolio_status(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    return filter_bitcoin_portfolio(portfolio_status)

# GPT 요청 처리 및 응답
def handle_gpt_request(final_result):
    json_result = convert_to_json(final_result)
    formatted_input = format_input(json_result)
    request_data = prepare_request(formatted_input)
    response_content = send_request(request_data)

    # reason 번역 처리
    if "reason" in response_content:
        try:
            translated_reason = GoogleTranslator(source="en", target="ko").translate(response_content["reason"])
            response_content["reason"] = translated_reason
        except Exception as e:
            print(f"번역 중 오류 발생: {e}")

    # `amount` 값 처리
    try:
        amount = response_content.get("amount")
        if amount:
            # 문자열에서 불필요한 단위 제거 및 숫자로 변환
            if "KRW" in amount or "BTC" in amount:
                amount = float(amount.replace(" KRW", "").replace(" BTC", "").strip())
            else:
                amount = float(amount.strip())  # 단위가 없는 경우
            response_content["amount"] = amount  # 변환된 값으로 업데이트
        else:
            response_content["amount"] = None
    except ValueError as ve:
        print(f"Invalid amount format in GPT response: {response_content.get('amount')}")
        response_content["amount"] = None

    return response_content


# 매매 실행 및 로깅
def execute_trade_and_log(action, amount, current_price, response_content):
    market = "KRW-BTC"
    trade_result = execute_trade(action, amount, market)
    log_transaction(action, trade_result)

    return {
        "timestamp": get_current_time(),
        "action": action,
        "currency": market,
        "amount": amount,
        "price": current_price,
        "total_value": amount * current_price,
        "reason": response_content.get("reason"),
    }

# Slack 알림 생성 및 전송
def send_slack_notification(db, gpt_result, response_content, calc_result, portfolio_data):
    notifier = SlackNotifier()

    # 누적 데이터 계산 (갱신된 값을 가져옴)
    cumulative_summary = calculate_cumulative_profit_and_rate(db)

    # 최근 거래 로그 가져오기
    last_trade_log = get_last_trade_log(db)

    # Slack 데이터 생성
    slack_data = {
        "executed_action": gpt_result[0] if gpt_result and gpt_result[0] != "hold" else "hold",
        "executed_reason": response_content.get("reason", "정보 없음"),
        "profit_rate": f"{calc_result.get('profit_rate', 0.0):.2f}%",
        "profit_amount": f"{calc_result.get('profit_loss', 0.0):,.2f} KRW",
        "balance": f"{portfolio_data.get('target_asset', {}).get('balance', 0.0):.8f} BTC",
        "cash_balance": f"{float(portfolio_data.get('cash_balance', 0.0)):.2f} KRW",
        "investment": f"{portfolio_data.get('target_asset', {}).get('total_investment', 0.0):,.2f} KRW",
        "cumulative_profit_amount": f"{cumulative_summary.get('cumulative_profit_loss', 0.0):,.2f} KRW",
        "cumulative_profit_rate": f"{cumulative_summary.get('cumulative_profit_rate', 0.0):.2f}%",
        "last_trade_time": last_trade_log.timestamp.isoformat() if last_trade_log else "N/A",
        "last_action": last_trade_log.action if last_trade_log else "N/A",
        "last_trade_amount": f"{last_trade_log.amount:.8f} BTC" if last_trade_log else "0 BTC",
        "last_trade_reason": last_trade_log.reason if last_trade_log else "정보 없음",
    }

    # 디버깅 출력
    print("\n[Slack Data]:", slack_data)
    print("[Portfolio Status]:", portfolio_data)
    print("[Cumulative Summary]:", cumulative_summary)

    # Slack 메시지 전송
    if notifier.check_connection():
        formatted_message = notifier.format_slack_message(slack_data)
        notifier.send_message("#autobitcoin", formatted_message)


# 비즈니스 로직
def business_logic():
    db = SessionLocal()
    try:
        # 데이터 수집
        current_time = get_current_time()
        market_data = collect_market_data()

        # 포트폴리오 상태 조회
        portfolio_status = get_portfolio_status()

        # 최종 데이터 구성
        final_result = {
            "timestamp": current_time,
            "portfolio": portfolio_status,
            "market_data": market_data,
        }

        # GPT 요청 및 응답 처리
        response_content = handle_gpt_request(final_result)

        # 매매 결정
        gpt_result = make_decision(response_content, portfolio_status)
        calc_result = calculate_profit_loss(portfolio_status, market_data["current_price"])

        # 매매 실행
        if gpt_result[0] != "hold":
            trade_log = execute_trade_and_log(
                gpt_result[0], gpt_result[1], market_data["current_price"], response_content
            )
            create_trade_log(db, trade_log)

        # 포트폴리오 상태 갱신
        portfolio_status = get_portfolio_status()
        print("\n[Portfolio Status]:", portfolio_status)

        # 누적 데이터 업데이트
        update_cumulative_summary(
            db,
            new_profit_loss=calc_result.get("profit_loss", 0.0),
            new_profit_rate=calc_result.get("profit_rate", 0.0),
        )

        # Slack 알림 전송
        send_slack_notification(db, gpt_result, response_content, calc_result, portfolio_status)

    except Exception as e:
        print(f"\n[Error in Business Logic]: {e}")
    finally:
        db.close()
# 스케줄러 실행
def run_scheduler():
    schedule.every(60).minutes.do(business_logic)
    business_logic()  # 첫 실행
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    initialize_env()
    init_db()
    run_scheduler()
