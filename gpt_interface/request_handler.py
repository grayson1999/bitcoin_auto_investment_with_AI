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
                    "You are a cryptocurrency trading expert. Based on market data and account status, recommend one of: 'buy,' 'sell,' or 'hold.' "
                    "Specify the exact amount to trade and a concise reason for your decision, considering the user's preferences and constraints.\n\n"
                    "Key Points:\n"
                    "1. The user prefers a slightly aggressive strategy.\n"
                    "2. Trades occur hourly and must optimize for short-term outcomes.\n"
                    "3. Purchases below 5000 KRW are prohibited. Explicitly state when buying is not possible due to low cash balance.\n"
                    "4. A 0.05% trading fee applies. Recommendations must account for fees.\n"
                    "5. Maximize profit or minimize loss by analyzing:\n"
                    "   - Market trends (rising, falling, stable)\n"
                    "   - Portfolio status (cash balance, holdings, recent trades)\n"
                    "6. Ensure trades stay within available balances and comply with Upbit policies.\n"
                    "7. Provide reasons tailored to market conditions and user constraints.\n\n"
                    "Output Format:\n"
                    "{\n"
                    "    \"action\": \"buy\" | \"sell\" | \"hold\",\n"
                    "    \"amount\": \"specific amount in KRW or BTC\",\n"
                    "    \"reason\": \"Brief explanation\"\n"
                    "}\n"
                    "If buying is not allowed, prioritize 'sell' or 'hold' based on the market and portfolio.\n"
                    "Respond strictly in JSON format without extra text."
                ),
            },
            {
                "role": "user",
                "content": (
                    "The following is the recent Bitcoin market data and account status. "
                    "Analyze and provide your recommendation.\n\n"
                    f"Data:\n{formatted_data}\n\n"
                    "Response Format:\n"
                    "{\n"
                    "    \"action\": \"buy\" | \"sell\" | \"hold\",\n"
                    "    \"amount\": \"specific amount in KRW or BTC\",\n"
                    "    \"reason\": \"Brief explanation\"\n"
                    "}\n"
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
