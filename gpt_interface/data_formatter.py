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
                f"    - Balance: {asset['balance']}\n"
                f"    - Avg Buy Price: {asset['avg_buy_price']} KRW\n"
            )
        else:
            formatted_data += "  Target Asset: None\n"

        # Market Data 정보 포맷팅
        formatted_data += (
            f"\nMarket Data:\n"
            f"- Current Price: {data['market_data']['current_price']} KRW\n"
            f"- 24h Volume: {data['market_data']['volume_24h']}\n"
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

        # 15분 요약 데이터 정보 추가
        formatted_data += "\n15-Minute Summary (aggregated from 5-minute data):\n"
        for segment, segment_data in data["market_data"]["processed_5min"].items():
            if segment == "overall":
                formatted_data += (
                    f"  Overall:\n"
                    f"    - Trend: {segment_data['trend']}\n"
                    f"    - Max Volatility: {segment_data['max_volatility']}\n"
                    f"    - Outlier Count: {segment_data['outlier_count']}\n"
                )
            else:
                formatted_data += (
                    f"  {segment}:\n"
                    f"    - Avg Price: {segment_data['avg_price']} KRW\n"
                    f"    - High: {segment_data['high_price']} KRW\n"
                    f"    - Low: {segment_data['low_price']} KRW\n"
                    f"    - Volatility: {segment_data['volatility']}\n"
                    f"    - VWAP: {segment_data['vwap']} KRW\n"
                    f"    - Total Volume: {segment_data['total_vol']}\n"
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

