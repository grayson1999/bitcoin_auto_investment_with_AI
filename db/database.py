from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base  # Base를 base.py에서 가져옵니다.
import os
from dotenv import load_dotenv

# 현재 파일의 디렉토리를 기준으로 .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")

# .env 파일 로드
load_dotenv()

# 환경 변수에서 PostgreSQL 데이터베이스 URL 가져오기
# 예: "postgresql://username:password@localhost:5432/dbname"
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from . import models  # models를 여기서 import
    Base.metadata.create_all(bind=engine)

# 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
