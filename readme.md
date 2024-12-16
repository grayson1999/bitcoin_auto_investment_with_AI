![Python](https://img.shields.io/badge/Python-3.9-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange)
![Slack](https://img.shields.io/badge/Slack-API-green)
![Upbit](https://img.shields.io/badge/Upbit-API-yellow)

# 💰 **bitcoin_auto_investment**

## 🌐 프로젝트 설명
`bitcoin_auto_investment`는 OpenAI의 GPT 모델과 업비트 API를 활용하여 비트코인 자동 매매를 실행하는 프로그램입니다. 프로그램은 실시간 데이터를 수집, 분석하여 매수(buy), 매도(sell), 또는 보유(hold) 결정을 내리고 이를 Slack 알림을 통해 전달합니다. 또한, 투자 내역 및 성과를 데이터베이스에 기록하여 지속적인 성능 분석과 개선이 가능합니다.

## 🔧 **프로젝트 설치 및 실행 방법**

### 1. 개발 환경 설정

```bash
# 1. 레포지토리 클론
$ git clone https://github.com/grayson1999/gpt-bitcoin.git
$ cd gpt-bitcoin

# 2. Python 개발 환경 설정
$ python3 -m venv venv
$ source venv/bin/activate   # Windows 경우: venv\Scripts\activate
$ pip install -r requirements.txt

# 3. PostgreSQL Docker Container 실행
$ docker run --name bitcoin-db \
  -e POSTGRES_USER=grayson \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=bitcoin \
  -p 5432:5432 -d postgres

# 4. .env 파일 생성 및 설정
$ cp .env.example .env
# .env 파일 내부에 Upbit, OpenAI, Slack API 키 설정
```

### 2. 프로그램 실행

```bash
# 데이터베이스 초기화
$ python -m db.make_db

# 자동매매 스케줄러 실행
$ python main.py
```

## 🔬 비즈니스 로직

### 동작 과정

```plaintext
1. 데이터 수집:
   - 업비트 API에서 실시간 비트코인 가격, 거래량, 과거 데이터 수집
   - 30일 및 5분 봉 데이터를 전처리

2. 포트폴리오 상태 조회:
   - 현재 보유 자산 (BTC, KRW 잔액) 확인

3. GPT 분석:
   - 수집된 데이터를 GPT 모델에 입력
   - 매수, 매도, 보유 중 하나의 결정을 반환

4. 매매 실행:
   - GPT 결과에 따라 매수/매도 실행
   - Slack 알림 전송

5. 데이터 저장 및 누적 분석:
   - 거래 결과와 수익률을 데이터베이스에 저장
   - 누적 수익 데이터 갱신
```

### 데이터 수집 및 전처리

수집된 데이터는 **정량적 데이터**와 **정성적 데이터**로 나뉘며, 현재는 정량적 데이터만을 활용하고 있습니다. 정성적 데이터는 향후 개발 예정입니다.

---

#### 📊 **정량적 데이터**
업비트 API를 통해 실시간으로 수집되는 주요 정량적 데이터는 다음과 같습니다:

1. **현재 비트코인 가격**
   - `fetch_current_price` 함수로 호출
   - 시장 상황에 따른 최신 비트코인 가격을 수집
   - 데이터 형태: `float` (예: 151000000.0 KRW)

2. **24시간 거래량**
   - `fetch_24h_volume` 함수로 호출
   - 최근 24시간 동안의 비트코인 거래량을 제공
   - 데이터 형태: `float` (예: 1200.0 BTC)

3. **30일 일봉 데이터**
   - `fetch_30d_candlestick` 함수로 호출
   - 과거 30일 동안의 일봉 데이터를 포함:
     - 시가(Open), 종가(Close), 최고가(High), 최저가(Low), 거래량(Volume)
   - 데이터 형태: `DataFrame` (열: `open`, `close`, `high`, `low`, `volume`)

4. **최근 3시간 5분 봉 데이터**
   - `fetch_5min_data` 함수로 호출
   - 최근 3시간 동안의 5분 간격 데이터를 포함:
     - 평균 가격, 변동성, 총 거래량
   - 데이터 형태: `DataFrame` (열: `open`, `close`, `high`, `low`, `volume`)

---

#### 🛠️ **데이터 전처리**
수집된 데이터는 다음 단계를 거쳐 **GPT 입력 형식**에 적합하도록 가공됩니다:

1. **결측치 처리**
   - 모든 데이터의 결측값(NaN)은 `0` 또는 통계적 평균값으로 대체.
   - 처리 함수: `handle_missing_values`

2. **정규화**
   - 분석에 필요한 열("close", "volume")만 남기고 불필요한 데이터 제거.
   - 처리 함수: `normalize_data`

3. **핵심 데이터 추출**
   - 기간별(예: 7일, 10일)로 데이터를 나눠 평균값, 최대값, 최소값, 변동성을 계산.
   - 데이터 요약 예:
  
    ```json
     {
       "segment_1": {
         "date_range": "2024-12-01 to 2024-12-07",
         "average_price": 150000000.0,
         "high_price": 151000000.0,
         "low_price": 149000000.0,
         "volatility": 0.015
       }
         ...

        "hour_1": {
        "avg_price": 151200000.0,
        "high_price": 151300000.0,
        "low_price": 151100000.0,
        "volatility": 0.005,
        "total_vol": 200.0
      }
     }
    ```

   - 처리 함수: `extract_relevant_data`

4. **포트폴리오 필터링**
   - 보유한 자산(BTC)과 현금 잔고(KRW)을 필터링하여 GPT에 전달.
   - 처리 함수: `filter_bitcoin_portfolio`
   - 필터링된 데이터 예:
  
     ```json
     {
       "cash_balance": 50000.0,
       "target_asset": {
         "currency": "BTC",
         "balance": 0.0003,
         "avg_buy_price": 150000000.0
       }
     }
     ```

---

#### 💡 **전처리 후 GPT 입력 데이터 예시**

```json
{
  "timestamp": "2024-12-16T10:15:00+09:00",
  "portfolio": {
    "cash_balance": 45000.0,
    "target_asset": {
      "currency": "BTC",
      "balance": 0.0003,
      "avg_buy_price": 151000000.0,
      "total_investment": 45300.0
    }
  },
  "market_data": {
    "current_price": 151250000.0,
    "volume_24h": 1300.0,
    "summary_30d": {
      "average_price": 150000000.0,
      "volatility": 0.012
    },
    "processed_5min": {
      "hour_1": {
        "avg_price": 151200000.0,
        "high_price": 151300000.0,
        "low_price": 151100000.0,
        "volatility": 0.005,
        "total_vol": 200.0
      },
      "overall": {
        "trend": "up",
        "max_volatility": 0.01,
        "outlier_count": 2
      }
    }
  }
}
```

---

#### 🚀 **결과 출력: Slack 알림 예시**

```plaintext
🔔 **[비트코인 투자 알림]**

📋 **실행 요약**
➡️ **이번 행위**: sell
💡 **행위 이유**: 현재 시장 추세는 하락하고 있으며, 매도하여 손실을 줄이는 것이 좋습니다.

📊 **수익 요약**
💵 **이번 수익 금액**: 2.97 KRW
📈 **이번 수익률**: 0.01%
💰 **누적 수익 금액**: 2.31 KRW
📉 **누적 수익률**: 0.00%

💼 **포트폴리오 현황**
🪙 **보유 자산 (BTC)**: 0.0000 BTC
💵 **원화 잔고**: 60726.80 KRW
💳 **총 투자 금액**: 0.00 KRW

📋 **거래 내역**
📅 **마지막 거래 시간**: 2024-12-16 23:29:19
🔄 **거래 액션**: sell (0.00033030 BTC)
💡 **거래 이유**: 현재 시장 추세는 하락 중이며 변동성이 더 높은 것으로 관찰되었습니다.
```

## 🔖 폴더 구조

```plaintext
project_root/
├── data_collection/
│   ├── fetch_quantitative.py
│   ├── preprocess.py
├── gpt_interface/
│   ├── request_handler.py
│   ├── decision_logic.py
├── trade_manager/
│   ├── account_status.py
│   ├── trade_handler.py
├── db/
│   ├── models.py
│   ├── crud.py
│   ├── database.py
├── notifications/
│   ├── slack_notifier.py
├── tests/
├── .env
├── requirements.txt
├── main.py
```
