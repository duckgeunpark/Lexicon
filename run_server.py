"""
Lexicon - FastAPI + PyWebView 데스크톱 앱
"""
import os
import sys
import threading
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webview

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# FastAPI 앱 초기화
app = FastAPI(title="Lexicon API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 경로 설정
STATIC_DIR = Path(__file__).parent / "static"

# 정적 파일이 없으면 생성
if not STATIC_DIR.exists():
    print(f"경고: {STATIC_DIR} 폴더가 없습니다.")
    print(f"경로: {STATIC_DIR.absolute()}")
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
else:
    print(f"✓ Static 폴더 찾음: {STATIC_DIR.absolute()}")

# ============ API 엔드포인트 ============

# API 엔드포인트 로드
api_loaded = False
try:
    from app.api.endpoints.quiz import router as quiz_router
    from app.api.endpoints.settings import router as settings_router
    app.include_router(quiz_router, prefix="/api/quiz")
    app.include_router(settings_router, prefix="/api/settings")
    print("✓ API 엔드포인트 로드됨")
    api_loaded = True
except ImportError as e:
    print(f"⚠️  API 엔드포인트 로드 실패: {e}")
    print("   → API 없이 정적 파일만 제공합니다")

# ============ 정적 파일 서빙 ============

# 정적 파일 마운트 (CSS, JS, 이미지 등) - 먼저 마운트
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print(f"✓ 정적 파일 마운트됨: /static → {STATIC_DIR}")

# index.html 라우트
@app.get("/")
async def read_root():
    """메인 페이지"""
    return FileResponse(STATIC_DIR / "index.html")

# ============ 서버 실행 ============

def run_uvicorn_server():
    """Uvicorn 서버를 백그라운드에서 실행"""
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True,
        use_colors=True
    )

def start_webview():
    """PyWebView 데스크톱 앱 시작"""
    time.sleep(2)
        
    window = webview.create_window(
        title='Lexicon',
        url='http://127.0.0.1:8000',
        width=800,
        height=600,
        min_size=(700, 500),
        resizable=True,
        fullscreen=False,
        background_color='#f5f5f5',

    )
    
    webview.start(debug=False)

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 Lexicon 데스크톱 앱 시작 중...")
    print("=" * 50)

    # FastAPI 서버를 백그라운드 스레드에서 실행
    server_thread = threading.Thread(target=run_uvicorn_server, daemon=True)
    server_thread.start()

    print("✓ FastAPI 서버 시작됨 (http://127.0.0.1:8000)")

    # PyWebView 시작 (메인 스레드)
    try:
        start_webview()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
