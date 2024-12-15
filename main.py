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
from db.crud import create_investment_summary, create_trade_log, create_portfolio, create_gpt_log
from notifications.slack_notifier import SlackNotifier
from deep_translator import GoogleTranslator


# 환경 변수 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# API 키 설정
UPBIT_ACCESS_KEY = os.getenv("UPBIT_API_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_API_SECRET")

# SlackNotifier 초기화
notifier = SlackNotifier()

# 데이터베이스 초기화
init_db()

# 현재 시간 (서울 기준) 가져오기
seoul_tz = pytz.timezone("Asia/Seoul")
current_datetime = datetime.datetime.now(seoul_tz).isoformat()

# DB 저장할 데이터 초기화
db = SessionLocal()
gpt_log_data = {}
trade_log_data = {}
portfolio_data = {}
summary_data = {}

try:
    # 1. 데이터 수집
    current_price = fetch_current_price()  # 현재 비트코인 가격
    volume_24h = fetch_24h_volume()  # 24시간 거래량

    # 30일 일봉 데이터 처리
    candlestick_30d = fetch_30d_candlestick()
    if candlestick_30d is not None:
        cleaned_30d = handle_missing_values(candlestick_30d)
        normalized_30d = normalize_data(cleaned_30d)
        summary_30d = extract_relevant_data(normalized_30d)
    else:
        summary_30d = {"error": "Failed to fetch 30-day candlestick data"}

    # 5분 봉 데이터 처리 (3시간)
    raw_5min_data = fetch_5min_data()
    if raw_5min_data is not None:
        cleaned_5min = handle_missing_values(raw_5min_data)
        processed_5min = preprocess_5min_data(cleaned_5min)
    else:
        processed_5min = {"error": "Failed to fetch 5-minute candlestick data"}

    # 2. 포트폴리오 상태 조회
    portfolio_status = fetch_portfolio_status(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    filtered_portfolio = filter_bitcoin_portfolio(portfolio_status)

    # 3. 최종 데이터 구성
    final_result = {
        "timestamp": current_datetime,
        "portfolio": filtered_portfolio,
        "market_data": {
            "current_price": current_price,
            "volume_24h": volume_24h,
            "summary_30d": summary_30d,
            "processed_5min": processed_5min,
        },
    }

    # 4. 데이터 전처리 및 GPT 요청 준비
    json_result = convert_to_json(final_result)
    formatted_input = format_input(json_result)
    request_data = prepare_request(formatted_input)

    # 5. GPT API 호출 및 응답 처리
    response_content = send_request(request_data)
    
    # 5.1 GPT API 응답 처리 및 reason 번역
    if "reason" in response_content:
        try:
            # 영어에서 한국어로 번역
            translated_reason = GoogleTranslator(source="en", target="ko").translate(response_content["reason"])
            print("Translated Reason:", translated_reason)

            # reason 대체
            response_content["reason"] = translated_reason
        except Exception as e:
            print(f"번역 중 오류 발생: {e}")

    # GPT 로그 데이터 저장 준비
    gpt_log_data = {
        "timestamp": current_datetime,
        "input_data": formatted_input,
        "action": response_content.get("action"),
        "amount": float(response_content.get("amount").replace(" KRW", "")) if response_content.get("amount") else None,
        "reason": response_content.get("reason"),
    }

    # 6. GPT 응답 기반으로 매매 결정
    gpt_result = make_decision(response_content, filtered_portfolio)
    print(gpt_result)

    # 7. 매매 실행 및 로깅
    if gpt_result[0] != "hold":
        action, amount = gpt_result
        market = "KRW-BTC"

        trade_result = execute_trade(action, amount, market)
        log_transaction(action, trade_result)

        # 거래 로그 데이터 저장 준비
        trade_log_data = {
            "timestamp": current_datetime,
            "action": action,
            "currency": market,
            "amount": amount,
            "price": current_price,
            "total_value": amount * current_price,
            "reason": response_content.get("reason"),
        }

    # 8. 수익률 계산
    calc_result = calculate_profit_loss(filtered_portfolio, current_price)
    print(calc_result)

    # 포트폴리오 데이터 저장 준비
    if filtered_portfolio.get("target_asset"):
        target_asset = filtered_portfolio["target_asset"]
        portfolio_data = {
            "currency": target_asset.get("currency", "N/A"),
            "balance": target_asset.get("balance", 0.0),
            "avg_buy_price": target_asset.get("avg_buy_price", 0.0),
            "total_investment": target_asset.get("total_investment", 0.0),
        }
    else:
        portfolio_data = {
            "currency": "N/A",
            "balance": 0.0,
            "avg_buy_price": 0.0,
            "total_investment": 0.0,
        }

    # 투자 요약 데이터 저장 준비
    summary_data = {
        "start_date": current_datetime,  # 현재 실행 시점 (단일 실행 기준)
        "end_date": None,  # 프로그램 종료 시 설정 가능
        "total_investment": portfolio_data["total_investment"],
        "total_profit_loss": calc_result["profit_loss"],
        "profit_rate": calc_result["profit_rate"],
        "total_trades": 1,  # 단일 실행 기준
    }

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    # DB 저장
    try:
        if gpt_log_data:
            create_gpt_log(db, gpt_log_data)
        if trade_log_data:
            create_trade_log(db, trade_log_data)
        if portfolio_data:
            create_portfolio(db, portfolio_data)
        if summary_data:
            create_investment_summary(db, summary_data)

        db.commit()

        try:
            # Slack 알림 데이터 구성
            slack_data = {
                "executed_action": gpt_result[0] if gpt_result and gpt_result[0] != "hold" else "hold",  # 이번 실행의 행위 ('buy', 'sell', 'hold')
                "executed_reason": response_content.get("reason", "정보 없음"),
                "profit_rate": f"{calc_result.get('profit_rate', 0.0):.2f}%" if calc_result else "0.0%",
                "profit_amount": f"{calc_result.get('profit_loss', 0.0):,.2f} KRW" if calc_result else "0.00 KRW",  # 수익 금액 추가
                "balance": f"{portfolio_data.get('balance', 0.0):.8f} BTC" if portfolio_data.get("balance") else "0 BTC",
                "cash_balance": f"{float(filtered_portfolio.get('cash_balance', 0.0)):.2f} KRW" if filtered_portfolio else "0 KRW",
                "investment": f"{float(portfolio_data.get('total_investment', 0.0)):.2f} KRW" if portfolio_data.get("total_investment") else "0 KRW",
                "last_trade_time": trade_log_data.get("timestamp", "N/A"),
                "last_action": trade_log_data.get("action", "N/A"),
                "last_trade_amount": f"{trade_log_data.get('amount', 0.0):.8f} BTC" if trade_log_data.get("amount") else "0 BTC",
                "last_trade_reason": trade_log_data.get("reason", "정보 없음"),
            }


            
            print("Slack Data:", slack_data)  # 알림 데이터 확인

            # Slack 메시지 전송
            if notifier.check_connection():
                formatted_message = notifier.format_slack_message(slack_data)
                notifier.send_message("#autobitcoin", formatted_message)
        except Exception as e:
            print(f"Slack 알림 중 오류 발생: {e}")

    except Exception as db_error:
        print(f"DB 저장 중 오류 발생: {db_error}")
    finally:
        db.close()
