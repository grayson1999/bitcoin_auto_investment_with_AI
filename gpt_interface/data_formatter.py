import logging
from typing import Dict, Union

import json
from typing import Dict

def format_input(data: Dict) -> str:
    """
    데이터를 GPT 입력 형식에 적합하도록 포맷팅합니다.
    :param data: Dict - 전처리된 데이터.
    :return: str - GPT 모델에 전달할 입력 데이터 텍스트.
    """
    try:
        # JSON 문자열일 경우 딕셔너리로 파싱
        if isinstance(data, str):
            data = json.loads(data)
        
        # Portfolio 정보 포맷팅
        formatted_data = (
            f"Portfolio:\n"
            f"- Cash Balance: {data['portfolio']['cash_balance']} KRW\n"
        )
        if data["portfolio"].get("target_asset"):
            asset = data["portfolio"]["target_asset"]
            formatted_data += (
                f"  Target Asset:\n"
                f"    - Currency: {asset['currency']}\n"
                f"    - Balance: {asset['balance']} BTC\n"
                f"    - Avg Buy Price: {asset['avg_buy_price']} KRW\n"
            )
        else:
            formatted_data += "  Target Asset: None\n"

        # Market Data 정보 포맷팅
        formatted_data += (
            f"\nMarket Data:\n"
            f"- Current Price: {data['market_data']['current_price']} KRW\n"
            f"- 24h Volume: {data['market_data']['volume_24h']} BTC\n"
            f"\n30-Day Summary:\n"
        )
        for segment, segment_data in data["market_data"]["summary_30d"].items():
            formatted_data += (
                f"  {segment}:\n"
                f"    - Date Range: {segment_data['date_range']}\n"
                f"    - Avg Price: {segment_data['average_price']} KRW\n"
                f"    - High: {segment_data['high_price']} KRW\n"
                f"    - Low: {segment_data['low_price']} KRW\n"
                f"    - Volatility: {segment_data['volatility']}\n"
            )

        # 5분 봉 요약 포맷팅
        formatted_data += "\n5-Minute Summary:\n"
        for hour, hour_data in data["market_data"]["processed_5min"].items():
            if hour == "overall":
                formatted_data += (
                    f"  Overall:\n"
                    f"    - Trend: {hour_data['trend']}\n"
                    f"    - Max Volatility: {hour_data['max_volatility']}\n"
                    f"    - Outlier Count: {hour_data['outlier_count']}\n"
                )
            else:
                formatted_data += (
                    f"  {hour}:\n"
                    f"    - Avg Price: {hour_data['avg_price']} KRW\n"
                    f"    - High: {hour_data['high_price']} KRW\n"
                    f"    - Low: {hour_data['low_price']} KRW\n"
                    f"    - Volatility: {hour_data['volatility']}\n"
                    f"    - VWAP: {hour_data['vwap']} KRW\n"
                    f"    - Total Volume: {hour_data['total_vol']} BTC\n"
                )

        return formatted_data.strip()
    except Exception as e:
        raise ValueError(f"입력 데이터 포맷팅 중 오류 발생: {e}")





def parse_response(response: str) -> Dict:
    """
    GPT 응답 데이터를 파싱하여 핵심 정보를 추출합니다.
    :param response: str - GPT 응답 텍스트.
    :return: Dict - 매수/매도/보류 판단 및 관련 데이터.
    """
    try:
        response_data = eval(response)  # 문자열을 딕셔너리로 변환
        if not isinstance(response_data, dict):
            raise ValueError("응답 데이터가 유효한 딕셔너리 형식이 아닙니다.")
        if "action" not in response_data or "amount" not in response_data or "reason" not in response_data:
            raise ValueError("응답 데이터에 필요한 필드가 없습니다.")
        return response_data
    except Exception as e:
        raise ValueError(f"응답 데이터 파싱 중 오류 발생: {e}")


def handle_errors(error: Exception) -> str:
    """
    데이터 처리 및 응답 파싱 과정에서 발생하는 오류를 처리합니다.
    :param error: Exception - 발생한 예외.
    :return: str - 사용자 친화적인 에러 메시지.
    """
    logging.error(f"오류 발생: {error}")
    return "An error occurred during data processing. Please try again later."


if __name__ == "__main__":
    # 테스트 데이터
    test_data = {
        "current_price": 144300000.0,
        "volume_24h": 2236.49046605,
        "summary_30d": {
            "segment_1": {
                "date_range": "2024-11-14 09:00:00 to 2024-11-20 09:00:00",
                "average_price": 127913285.71428572,
                "high_price": 133180000.0,
                "low_price": 123572000.0,
                "volatility": 2981471.488727544,
            }
        },
        "processed_5min": {
            "hour_1": {
                "average_price": 143833500.0,
                "high_price": 144200000.0,
                "low_price": 143351000.0,
                "volatility": 165284.60303367642,
                "volume_weighted_avg_price": 143888625.14067563,
                "total_volume": 170.35494666,
            },
            "overall": {
                "overall_trend": "upward",
                "max_volatility": 331419.5011074118,
            },
        },
    }

    # 입력 데이터 포맷팅
    try:
        formatted_input = format_input(test_data)
        print("Formatted Input:")
        print(formatted_input)
    except Exception as e:
        print(handle_errors(e))

    # GPT 응답 데이터 파싱
    test_response = '{"action": "buy", "amount": "0.0035", "reason": "The current price shows an upward trend."}'
    try:
        parsed_response = parse_response(test_response)
        print("Parsed Response:")
        print(parsed_response)
    except Exception as e:
        print(handle_errors(e))
