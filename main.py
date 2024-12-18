import schedule
import time
import os
import pytz
import logging
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
from datetime import datetime

# ==========================
# 로깅 설정
# ==========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 터미널 출력
        logging.FileHandler("application.log", encoding="utf-8"),  # 로그 파일 저장
    ]
)

# 환경 초기화
def initialize_env():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(BASE_DIR, ".env")
    load_dotenv(dotenv_path)
    logging.info("환경 변수가 초기화되었습니다.")

# 현재 시간 가져오기
def get_current_time():
    seoul_tz = pytz.timezone("Asia/Seoul")
    return datetime.now(seoul_tz).isoformat()

# 데이터 수집
def collect_market_data(market_name="KRW-BTC"):
    logging.info(f"데이터 수집 시작: {market_name}")
    current_price = fetch_current_price(market_name)
    volume_24h = fetch_24h_volume(market_name)
    candlestick_30d = fetch_30d_candlestick(market_name)

    if candlestick_30d is not None:
        cleaned_30d = handle_missing_values(candlestick_30d)
        normalized_30d = normalize_data(cleaned_30d)
        summary_30d = extract_relevant_data(normalized_30d)
    else:
        summary_30d = {"error": "30일 봉 데이터를 가져오는 데 실패했습니다."}

    raw_5min_data = fetch_5min_data(market_name)
    if raw_5min_data is not None:
        cleaned_5min = handle_missing_values(raw_5min_data)
        processed_5min = preprocess_15min_data(cleaned_5min)
    else:
        processed_5min = {"error": "5분 봉 데이터를 가져오는 데 실패했습니다."}

    logging.info("데이터 수집 완료")
    return {
        "current_price": current_price,
        "volume_24h": volume_24h,
        "summary_30d": summary_30d,
        "processed_5min": processed_5min,
    }

# GPT 요청 처리 및 응답
def handle_gpt_request(final_result, market_name="KRW-BTC"):
    logging.info("GPT 요청 처리 시작")
    json_result = convert_to_json(final_result)
    formatted_input = format_input(json_result)
    request_data = prepare_request(formatted_input)
    response_content = send_request(request_data)

    if "reason" in response_content:
        try:
            translated_reason = GoogleTranslator(source="en", target="ko").translate(response_content["reason"])
            response_content["reason"] = translated_reason
            logging.info(f"GPT 응답: {response_content}")
        except Exception as e:
            logging.error(f"번역 오류: {e}")

    try:
        amount = response_content.get("amount", 0)
        if isinstance(amount, str):
            if "KRW" in amount or "BTC" in amount or market_name.split("-")[1] in amount:
                amount = float(amount.replace(" KRW", "").replace(" BTC", "").strip().replace(" {}".format(market_name.split("-")[1]), "").strip())
            else:
                amount = float(amount.strip())
        elif isinstance(amount, (float, int)):
            amount = float(amount)
        else:
            raise ValueError("잘못된 금액 형식")
        response_content["amount"] = amount
    except ValueError as ve:
        logging.error(f"잘못된 금액 형식: {response_content.get('amount')} - {ve}")
        response_content["amount"] = 0.0

    return response_content

# 매매 실행 및 로깅
def execute_trade_and_log(action, amount, current_price, response_content, market_name="KRW-BTC"):
    logging.info(f"매매 실행: {action}, 금액: {amount}, 현재 가격: {current_price}")
    trade_result = execute_trade(action, amount, market_name)
    log_transaction(action, trade_result)

    currency = market_name.split("-")[1]

    trade_log = {
        "timestamp": get_current_time(),
        "action": action,
        "currency": currency,
        "amount": amount,
        "price": current_price,
        "total_value": amount * current_price,
        "reason": response_content.get("reason"),
    }

    logging.info(f"매매 로그 생성: {trade_log}")
    return trade_log

# Slack 알림 생성 및 전송
def send_slack_notification(db, trade_log, portfolio_status,performance_data, market_name="KRW-BTC"):
    notifier = SlackNotifier()
    currency = market_name.split("-")[1]
    cumulative_summary = calculate_cumulative_profit_and_rate(db)

    slack_data = {
        "executed_action": trade_log.get("action", "hold"),
        "executed_reason": trade_log.get("reason", "정보 없음"),
        "executed_amount": (
            f"{trade_log['amount']:.8f} {currency}"
            if trade_log["currency"] != "KRW"
            else f"{trade_log['amount']:,.2f} KRW"
        ),
        "total_value": f"{trade_log['total_value']:,.2f} KRW",
        "balance": f"{portfolio_status.get('target_asset', {}).get('balance', 0.0):.8f} {currency}",
        "cash_balance": f"{portfolio_status.get('cash_balance', 0.0):,.2f} KRW",
        "investment": f"{portfolio_status.get('target_asset', {}).get('total_investment', 0.0):,.2f} KRW",
        "profit_amount": f"{performance_data.get('profit', 0.0):,.2f} KRW",
        "profit_rate": f"{performance_data.get('profit_rate', 0.0):.2f}%",
        "cumulative_profit_amount": f"{performance_data.get('cumulative_profit', 0.0):,.2f} KRW",
        "cumulative_profit_rate": f"{performance_data.get('cumulative_profit_rate', 0.0):.2f}%",
    }

    if notifier.check_connection():
        formatted_message = notifier.format_slack_message(slack_data)
        notifier.send_message("#autobitcoin", formatted_message)
        logging.info("Slack 알림 전송 완료")
    else:
        logging.warning("Slack 연결 실패")

# 핵심 비즈니스 로직
def business_logic():
    db = SessionLocal()
    MARKET_NAME = "KRW-XRP"
    trade_log = None  # trade_log 초기화
    try:
        logging.info("비즈니스 로직 시작")

        current_time = get_current_time()
        market_data = collect_market_data(MARKET_NAME)
        portfolio_status = get_portfolio_status(MARKET_NAME)

        final_result = {
            "timestamp": current_time,
            "portfolio": portfolio_status,
            "market_data": market_data,
        }

        response_content = handle_gpt_request(final_result, MARKET_NAME)
        gpt_result = make_decision(
            response_content, portfolio_status, final_result["market_data"]["current_price"], MARKET_NAME
        )

        if gpt_result[0] != "hold":
            # 매매 로그 생성 및 저장
            try:
                trade_log = execute_trade_and_log(
                    gpt_result[0], gpt_result[1], market_data["current_price"], response_content, MARKET_NAME
                )
                create_trade(db, trade_log)
                logging.info(f"매매 로그 저장 성공: {trade_log}")
            except Exception as e:
                logging.error(f"매매 로그 저장 중 오류 발생: {e}")

        

        if gpt_result[0] != "hold":
            # 포트폴리오 상태 업데이트
            try:
                portfolio_status = get_portfolio_status(MARKET_NAME)
                portfolio_data = {
                    "timestamp": current_time,
                    "cash_balance": portfolio_status.get("cash_balance", 0),
                    "total_investment": portfolio_status.get("total_investment", 0),
                    "currency": portfolio_status.get("target_asset", {}).get("currency", "N/A"),
                    "target_asset_balance": portfolio_status.get("target_asset", {}).get("balance", 0),
                    "avg_buy_price": portfolio_status.get("target_asset", {}).get("avg_buy_price", 0),
                }
                update_portfolio(db, portfolio_data)
                logging.info("포트폴리오 상태 업데이트 성공")
            except Exception as e:
                logging.error(f"포트폴리오 상태 업데이트 중 오류 발생: {e}")

            # 수익률 및 누적 수익률 계산
            try:
                current_price = market_data["current_price"]
                target_asset = portfolio_status.get("target_asset", {})
                target_balance = target_asset.get("balance", 0)
                avg_buy_price = target_asset.get("avg_buy_price", 0)

                invested_value = target_balance * avg_buy_price
                current_value = target_balance * current_price
                profit_loss = current_value - invested_value
                profit_rate = (profit_loss / invested_value * 100) if invested_value > 0 else 0.0

                cumulative_summary = calculate_cumulative_profit_and_rate(db)
                cumulative_profit = cumulative_summary.get("cumulative_profit_loss", 0.0)
                cumulative_profit_rate = cumulative_summary.get("cumulative_profit_rate", 0.0)
                total_investment = portfolio_status.get("total_investment", 0)

                cumulative_profit += profit_loss
                cumulative_profit_rate = (cumulative_profit / total_investment * 100) if total_investment > 0 else 0.0

                performance_data = {
                    "timestamp": current_time,
                    "profit": profit_loss,
                    "profit_rate": profit_rate,
                    "cumulative_profit": cumulative_profit,
                    "cumulative_profit_rate": cumulative_profit_rate,
                }

                create_performance(db, performance_data)
                logging.info(f"수익률 데이터 저장 성공: {performance_data}")
            except Exception as e:
                logging.error(f"수익률 데이터 저장 중 오류 발생: {e}")

        # Slack 알림 전송
        if trade_log and gpt_result[0] != "hold":
            send_slack_notification(
                db=db,
                trade_log=trade_log,
                portfolio_status=portfolio_status,
                performance_data = performance_data,
                market_name=MARKET_NAME
            )
            logging.info("Slack 전송 완료")

        logging.info("비즈니스 로직 완료")

    except Exception as e:
        logging.error(f"비즈니스 로직 중 오류 발생: {e}")
    finally:
        db.close()



# 스케줄러 실행
def run_scheduler():
    schedule.every(15).minutes.do(business_logic)
    business_logic()  # 첫 실행
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    initialize_env()
    init_db()
    run_scheduler()
