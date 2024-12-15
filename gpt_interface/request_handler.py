import openai
from typing import Dict

# GPT API 요청 처리 모듈

import json
from typing import Dict

def prepare_request(data: Dict) -> Dict:
    """
    전처리된 데이터를 GPT API가 요구하는 형식으로 변환합니다.
    :param data: Dict - 전처리된 데이터.
    :return: Dict - GPT API 요청 데이터.
    """
    try:
        formatted_data = json.dumps(data, indent=4, ensure_ascii=False)
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a cryptocurrency trading expert. Based on the provided market data and account status, "
                    "analyze the current situation and recommend a trading action: 'buy,' 'sell,' or 'hold.' "
                    "Additionally, suggest a specific amount of cash or Bitcoin to trade. Provide a concise explanation "
                    "for your decision, considering the user's current position, cash, invested value, and trading preferences.\n\n"
                    "Important Notes:\n"
                    "- The user has a slightly aggressive investment preference.\n"
                    "- As per Upbit's policy, purchases below 5000 KRW are not allowed. If the user's cash balance is less than 5000 KRW, explicitly state that buying is not possible.\n"
                    "- A 0.05% trading fee is applied per transaction.\n"
                    "- Transactions must account for fees, so only the amount excluding fees can be used for trades.\n"
                    "- Recommendations should prioritize maximizing profit or minimizing loss, even with constraints like low cash balances.\n"
                    "- Reasons should be concise, friendly, and limited to a single line."
                ),
            },
            {
                "role": "user",
                "content": (
                    "The following is the recent Bitcoin market data and account status. "
                    "Analyze and provide your recommendation based on the constraints and preferences.\n\n"
                    f"Data:\n{formatted_data}\n\n"
                    "Response Format (choose one):\n"
                    "For 'buy':\n"
                    "{\n"
                    "    \"action\": \"buy\",\n"
                    "    \"amount\": \"specific amount in KRW\",\n"
                    "    \"reason\": \"The market looks favorable for buying, and the amount fits your strategy.\"\n"
                    "}\n\n"
                    "For 'sell':\n"
                    "{\n"
                    "    \"action\": \"sell\",\n"
                    "    \"amount\": \"specific amount in BTC\",\n"
                    "    \"reason\": \"Selling aligns with the market trend and your current asset status.\"\n"
                    "}\n\n"
                    "For 'hold':\n"
                    "{\n"
                    "    \"action\": \"hold\",\n"
                    "    \"amount\": \"0\",\n"
                    "    \"reason\": \"Holding is the best option given the current market and constraints.\"\n"
                    "}\n\n"
                    "- Note: If the user's cash balance is less than 5000 KRW, you must not recommend buying. Instead, evaluate 'sell' or 'hold' based on market conditions and the user's portfolio.\n"
                    "Always respond in one of the above JSON formats without any additional text."
                ),
            },
        ]

        
        return {"model": "gpt-4o-mini", "messages": messages}
    
    except Exception as e:
        raise ValueError(f"요청 데이터 생성 중 오류 발생: {e}")


def send_request(request_data: Dict) -> Dict:
    """
    GPT API에 요청 데이터를 전송하고 응답을 수신합니다.
    :param request_data: Dict - GPT 요청 데이터.
    :return: Dict - GPT 응답 데이터.
    """
    try:
        response = openai.chat.completions.create(
            model=request_data["model"],
            messages=request_data["messages"]
        )
        # 응답 내용을 JSON 형식으로 반환
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"응답 데이터를 JSON으로 변환하는 중 오류 발생: {e}")
    except Exception as e:
        raise ValueError(f"GPT 요청 처리 중 오류 발생: {e}")


def validate_response(response: Dict) -> bool:
    """
    GPT 응답 데이터의 유효성을 검사합니다.
    :param response: Dict - GPT 응답 데이터.
    :return: bool - 유효하면 True, 아니면 False.
    """
    try:
        if "choices" in response and len(response["choices"]) > 0:
            return True
        return False
    except Exception as e:
        raise ValueError(f"응답 유효성 검사 중 오류 발생: {e}")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    # 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(BASE_DIR, ".env")

    # .env 파일 로드
    load_dotenv()
    
    # OpenAI API 키 설정 (환경 변수에서 가져오기)
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # 예시 데이터 생성
    example_data = {
    "timestamp": "2024-12-14T04:38:45.942204+09:00",
    "current_price": 144300000.0,
    "volume_24h": 2236.49046605,
    "account_status": {
        "cash": 500000,
        "bitcoin": 0.0035,
        "invested_value": 505000,
        "current_position": "hold"
    },
    "market_data": {
        "summary_30d": {
            "segment_1": {
                "average_price": 127913285.71428572,
                "volatility": 2981471.488727544
            },
            "segment_4": {
                "average_price": 139569428.57142857,
                "volatility": 1900233.569603384
            }
        },
        "processed_5min": {
            "hour_1": {
                "average_price": 143833500.0,
                "volatility": 165284.60303367642
            },
            "overall_trend": "upward"
        }
    }
}

    try:
        # GPT 요청 데이터 준비
        request_data = prepare_request(example_data)

        # GPT 요청 전송
        response_content = send_request(request_data)

        # 응답 출력
        print("GPT 응답 데이터:")
        print(response_content)

    except Exception as e:
        print(f"오류 발생: {e}")
