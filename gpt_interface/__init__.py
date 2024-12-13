import os
import openai
from dotenv import load_dotenv

# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

# .env 파일 로드
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

openai.api_key = OPENAI_API_KEY

__all__ = [
    "request_handler",
    "data_formatter",
    "decision_logic"
]
