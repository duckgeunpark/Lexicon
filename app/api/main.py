from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .endpoints import quiz, settings, llm

# FastAPI 앱 생성
app = FastAPI(
    title="Quiz App API",
    description="다국어 매칭 퀴즈 앱 백엔드 API",
    version="1.0.0"
)

# CORS 설정 (Electron 프론트엔드와 통신)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 origin 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 이미지 정적 파일 서빙
images_path = Path(__file__).parent.parent.parent / "images"
if images_path.exists():
    app.mount("/images", StaticFiles(directory=str(images_path)), name="images")

# 라우터 등록
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM"])


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Quiz App API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "quiz-api"
    }
