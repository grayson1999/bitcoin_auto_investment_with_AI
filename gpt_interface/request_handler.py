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
                    "2. Trades occur every 15 minutes and must optimize for short-term outcomes.\n"
                    "3. Trades (both buy and sell) below 5000 KRW are prohibited. Explicitly state when trading is not possible due to constraints.\n"
                    "4. A 0.05% trading fee applies. Recommendations must account for fees.\n"
                    "5. Maximize profit or minimize loss by analyzing:\n"
                    "   - Market trends (rising, falling, stable)\n"
                    "   - Portfolio status (cash balance, holdings, recent trades)\n"
                    "6. Ensure trades stay within available balances and comply with Upbit policies.\n"
                    "7. Provide reasons tailored to market conditions and user constraints.\n"
                    "8. If the action cannot be executed due to market constraints (e.g., minimum amount requirements for both buying and selling), return 'hold' as the action.\n"
                    "9. Prioritize 'hold' over invalid trades when constraints are not met.\n\n"
                    "Output Format:\n"
                    "{\n"
                    "    \"action\": \"buy\" | \"sell\" | \"hold\",\n"
                    "    \"amount\": \"specific amount\",\n"
                    "    \"reason\": \"Brief explanation (1 sentence)\"\n"
                    "}\n"
                    "If trading cannot be executed due to market or portfolio constraints, clearly state 'hold' as the action and provide the reason in the specified format.\n"
                    "Respond strictly in JSON format without extra text."
                )
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
                    "    \"amount\": \"specific amount\",\n"
                    "    \"reason\": \"Brief explanation(1 sentence)\"\n"
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
