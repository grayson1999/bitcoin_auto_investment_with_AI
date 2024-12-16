import os
import requests
from dotenv import load_dotenv

# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

# 환경 변수 로드
load_dotenv()

# Slack API 토큰
SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
BASE_URL = "https://slack.com/api"


class SlackNotifier:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {SLACK_API_TOKEN}"}

    def check_connection(self) -> bool:
        """
        Slack API 연결 상태 확인.
        :return: bool - 연결 성공 여부.
        """
        try:
            response = requests.get(f"{BASE_URL}/auth.test", headers=self.headers)
            if response.status_code == 200 and response.json().get("ok"):
                print("Slack 연결 상태: 성공")
                return True
            else:
                print("Slack 연결 상태: 실패", response.json())
                return False
        except Exception as e:
            print(f"Slack 연결 상태 확인 중 오류 발생: {e}")
            return False

    def format_slack_message(self, data: dict) -> str:
        """
        데이터를 기반으로 Slack 메시지를 포맷팅.
        :param data: dict - 알림 데이터.
        :return: str - 포맷된 메시지.
        """
        try:
            message = (
                f"🔔 **[비트코인 투자 알림]**\n\n"
                f"📋 **실행 요약**\n"
                f"➡️ **이번 행위**: {data.get('executed_action', 'N/A')}\n"
                f"💡 **행위 이유**: {data.get('executed_reason', '정보 없음')}\n\n"
                f"📊 **수익 요약**\n"
                f"💵 **이번 수익 금액**: {data.get('profit_amount', 'N/A')}\n"
                f"📈 **이번 수익률**: {data.get('profit_rate', 'N/A')}%\n"
                f"💰 **누적 수익 금액**: {data.get('cumulative_profit_amount', 'N/A')}\n"
                f"📉 **누적 수익률**: {data.get('cumulative_profit_rate', 'N/A')}%\n\n"
                f"💼 **포트폴리오 현황**\n"
                f"🪙 **보유 자산 (BTC)**: {data.get('balance', 'N/A')}\n"
                f"💵 **원화 잔고**: {data.get('cash_balance', 'N/A')}\n"
                f"💳 **총 투자 금액**: {data.get('investment', 'N/A')}\n\n"
                f"📋 **거래 내역**\n"
                f"📅 **마지막 거래 시간**: {data.get('last_trade_time', 'N/A')}\n"
                f"🔄 **거래 액션**: {data.get('last_action', 'N/A')} "
                f"({data.get('last_trade_amount', 'N/A')})\n"
                f"💡 **거래 이유**: {data.get('last_trade_reason', '정보 없음')}\n"
            )

            return message
        except Exception as e:
            print(f"Slack 메시지 포맷팅 중 오류 발생: {e}")
            return "메시지 포맷팅 오류 발생"



    def send_message(self, channel: str, text: str) -> bool:
        """
        Slack 메시지 전송.
        :param channel: str - 메시지를 보낼 Slack 채널.
        :param text: str - 전송할 메시지 내용.
        :return: bool - 전송 성공 여부.
        """
        try:
            payload = {"channel": channel, "text": text}
            response = requests.post(f"{BASE_URL}/chat.postMessage", headers=self.headers, json=payload)
            if response.status_code == 200 and response.json().get("ok"):
                print("메시지 전송 성공")
                return True
            else:
                print("메시지 전송 실패", response.json())
                return False
        except Exception as e:
            print(f"Slack 메시지 전송 중 오류 발생: {e}")
            return False


# 모듈 테스트
if __name__ == "__main__":
    notifier = SlackNotifier()

    # 1. 연결 상태 확인
    if notifier.check_connection():
        # 2. 메시지 포맷 설정
        test_data = {
            "event": "비트코인 거래",
            "message": "비트코인이 목표가에 도달했습니다.",
            "timestamp": "2024-12-15 14:00:00",
        }
        formatted_message = notifier.format_message(test_data)

        # 3. 메시지 전송
        notifier.send_message("#autobitcoin", formatted_message)
