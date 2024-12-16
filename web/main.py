from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sys
import os

# 현재 디렉토리 기준으로 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from web.routes import dashboard
import uvicorn

app = FastAPI(title="Bitcoin Auto Trading Report")

# Static files 설정
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 라우터 등록
app.include_router(dashboard.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/api/dashboard" />')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)  # reload=False로 디버그 모드 비활성화