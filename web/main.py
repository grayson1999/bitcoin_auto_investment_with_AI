from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from web.routes import dashboard

app = FastAPI(title="Bitcoin Auto Trading Report")

# Static files 설정
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 라우터 등록
app.include_router(dashboard.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/api/dashboard" />')
