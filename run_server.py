"""
Lexicon - FastAPI + PyWebView 데스크톱 앱
"""
import io
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

# PyInstaller --noconsole 모드에서 stdout/stderr 처리
try:
    if sys.platform.startswith('win'):
        # 실행 파일 모드에서는 stdout/stderr이 None일 수 있음
        if sys.stdout is None or not hasattr(sys.stdout, 'write'):
            # 로그 파일로 리다이렉트
            log_dir = Path.home() / "Lexicon" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "app.log"
            sys.stdout = open(log_file, 'w', encoding='utf-8', buffering=1)
            sys.stderr = sys.stdout
        elif hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
            # 일반 실행 모드에서는 UTF-8 인코딩 적용
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
except Exception:
    # stdout 설정 실패 시 무시
    pass

# 안전한 print 함수로 내장 print 재정의
_original_print = print
def safe_print(*args, **kwargs):
    try:
        _original_print(*args, **kwargs)
    except (ValueError, AttributeError, OSError):
        pass  # stdout이 없거나 닫혀있으면 무시

# 내장 print를 안전한 버전으로 교체
import builtins
builtins.print = safe_print

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

# PyInstaller 실행 파일 경로 처리
def get_base_path():
    """실행 파일 또는 스크립트의 기본 경로 반환"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 실행 파일
        return Path(sys.executable).parent
    else:
        # 일반 Python 스크립트
        return Path(__file__).parent

def get_resource_path(relative_path):
    """번들된 리소스 파일 경로 반환 (static 등)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 임시 폴더에서 리소스 로드
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path

# 정적 파일 경로 설정 (번들된 리소스)
STATIC_DIR = get_resource_path("static")

if not STATIC_DIR.exists():
    print(f"경고: {STATIC_DIR} 폴더가 없습니다.")
    print(f"경로: {STATIC_DIR.absolute()}")
else:
    print(f"✓ Static 폴더 찾음: {STATIC_DIR.absolute()}")

# ============ 데이터 디렉토리 및 기본 파일 생성 ============

import json

# 데이터 폴더 경로 설정 (실행 파일 위치 기준)
BASE_DIR = get_base_path()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
print(f"✓ Data 폴더 생성/확인: {DATA_DIR.absolute()}")

# 기본 config.json 생성
config_file = DATA_DIR / "config.json"
if not config_file.exists():
    default_config = {
        "quiz_file": "quiz",
        "language1": "ja",
        "language2": "en",
        "question_pattern": "A>B",
        "random_patterns": {
            "A>B": True,
            "B>A": True,
            "img>A": False,
            "img>B": False,
            "img>A,B": False
        },
        "quiz_type": "random",
        "quiz_types": {
            "subjective": True,
            "multiple_choice": True
        },
        "order_mode": "random",
        "selected_categories": ["hiragana", "katakana"],
        "llm": {
            "model": "",
            "api_key": ""
        }
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)
    print(f"✓ 기본 config.json 생성: {config_file}")
else:
    print(f"✓ config.json 존재: {config_file}")

# 기본 quiz.json 생성
quiz_file = DATA_DIR / "quiz.json"
if not quiz_file.exists():
    default_quiz = {
        "hiragana": {
            "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
            "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
            "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
            "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
            "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
            "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
            "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
            "や": "ya", "ゆ": "yu", "よ": "yo",
            "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
            "わ": "wa", "を": "wo", "ん": "n"
        },
        "katakana": {
            "ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o",
            "カ": "ka", "キ": "ki", "ク": "ku", "ケ": "ke", "コ": "ko",
            "サ": "sa", "シ": "shi", "ス": "su", "セ": "se", "ソ": "so",
            "タ": "ta", "チ": "chi", "ツ": "tsu", "テ": "te", "ト": "to",
            "ナ": "na", "ニ": "ni", "ヌ": "nu", "ネ": "ne", "ノ": "no",
            "ハ": "ha", "ヒ": "hi", "フ": "fu", "ヘ": "he", "ホ": "ho",
            "マ": "ma", "ミ": "mi", "ム": "mu", "メ": "me", "モ": "mo",
            "ヤ": "ya", "ユ": "yu", "ヨ": "yo",
            "ラ": "ra", "リ": "ri", "ル": "ru", "レ": "re", "ロ": "ro",
            "ワ": "wa", "ヲ": "wo", "ン": "n"
        }
    }
    with open(quiz_file, 'w', encoding='utf-8') as f:
        json.dump(default_quiz, f, ensure_ascii=False, indent=2)
    print(f"✓ 기본 quiz.json 생성: {quiz_file}")
else:
    print(f"✓ quiz.json 존재: {quiz_file}")

# quiz_wrong.json 생성 (오답 노트)
quiz_wrong_file = DATA_DIR / "quiz_wrong.json"
if not quiz_wrong_file.exists():
    with open(quiz_wrong_file, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
    print(f"✓ 기본 quiz_wrong.json 생성: {quiz_wrong_file}")

# ============ API 엔드포인트 ============

# API 엔드포인트 로드
api_loaded = False
try:
    from app.api.endpoints.quiz import router as quiz_router
    from app.api.endpoints.settings import router as settings_router
    from app.api.endpoints.llm import router as llm_router
    app.include_router(quiz_router, prefix="/api/quiz")
    app.include_router(settings_router, prefix="/api/settings")
    app.include_router(llm_router, prefix="/api/llm")
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

# data 폴더 마운트 (이미지 파일 서빙)
if DATA_DIR.exists():
    app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
    print(f"✓ 데이터 폴더 마운트됨: /data → {DATA_DIR}")

# index.html 라우트
@app.get("/")
async def read_root():
    """메인 페이지"""
    return FileResponse(STATIC_DIR / "index.html")


# 서버 종료 엔드포인트
@app.post("/api/shutdown")
async def shutdown():
    """서버 종료 엔드포인트"""
    import threading

    def kill_server():
        time.sleep(0.5)  # 응답을 보낼 시간 확보
        os._exit(0)  # 프로세스 강제 종료

    # 백그라운드에서 서버 종료
    threading.Thread(target=kill_server, daemon=True).start()

    return {"success": True, "message": "Server shutting down..."}


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
        height=700,
        min_size=(800, 700),
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
