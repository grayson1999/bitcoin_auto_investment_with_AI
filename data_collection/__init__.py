# data_collection/__init__.py

# 모듈 초기화 파일
from dotenv import load_dotenv
import os

# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

# 환경변수 로드
load_dotenv(dotenv_path)

# 업비트 API 설정
UPBIT_API_KEY = os.getenv("UPBIT_API_KEY")
UPBIT_API_SECRET = os.getenv("UPBIT_API_SECRET")
# UPBIT_BASE_URL = "https://api.upbit.com/v1"

# 환경변수 유효성 검증
if not UPBIT_API_KEY or not UPBIT_API_SECRET:
    raise ValueError("환경 변수에 API 키가 설정되지 않았습니다.")
