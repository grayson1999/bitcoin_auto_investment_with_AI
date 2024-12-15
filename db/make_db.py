import sys
import os

# 프로젝트 루트를 sys.path에 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from db.database import init_db  # 변경된 import 경로


def main():
    """
    데이터베이스 초기화 및 테이블 생성.
    """
    try:
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error during database initialization: {e}")

if __name__ == "__main__":
    main()
