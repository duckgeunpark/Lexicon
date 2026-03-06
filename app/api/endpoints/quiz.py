import re
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
from ...utils.data_loader import quiz_loader
from ...models.requests import (
    CheckAnswerRequest, SaveWrongAnswerRequest, ProgressData, SessionStats
)


router = APIRouter()


# ============ 보안: 파일명 검증 ============

def _sanitize_filename(filename: str) -> str:
    """파일명에서 안전하지 않은 문자를 제거하고 경로 탐색을 방지
    비라틴 문자(한글, 일본어 등)도 허용
    """
    if not filename:
        return filename
    # 경로 구분자 제거
    filename = filename.replace('\\', '').replace('/', '')
    # 안전한 문자만 허용 (알파벳, 숫자, 하이픈, 언더스코어, 마침표, 유니코드 문자)
    filename = re.sub(r'[^\w\-.]', '', filename, flags=re.UNICODE)
    # 상위 디렉토리 이동 방지
    filename = filename.lstrip('.')
    return filename


def _get_data_dir() -> Path:
    """절대경로 기반 data 디렉토리 반환"""
    return quiz_loader._resolve_data_dir()


# ============ 답안 정규화 ============

def normalize_answer(text: str) -> str:
    """답안 정규화: 소문자 변환, 공백 정리"""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text


@router.get("/next")
async def get_next_question() -> Dict:
    """
    다음 퀴즈 문제 가져오기

    Returns:
        완전한 퀴즈 데이터 (question, options, type, pattern 등)
    """
    try:
        question = quiz_loader.generate_quiz_question()

        if question is None:
            raise HTTPException(status_code=404, detail="No quiz data available")

        return {
            "success": True,
            "data": question
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_data(filename: str = None) -> Dict:
    """
    데이터 및 설정 다시 로드

    Args:
        filename: 로드할 JSON 파일명 (선택적, 없으면 현재 파일 리로드)

    Returns:
        성공 여부 및 로드된 데이터 정보
    """
    try:
        if filename:
            filename = _sanitize_filename(filename)
        quiz_loader.reload(filename)

        return {
            "success": True,
            "message": "Data reloaded successfully",
            "current_file": quiz_loader.current_filename,
            "stats": {
                "quiz_items": len(quiz_loader.quiz_data),
                "available_images": len(quiz_loader.available_images),
                "config": quiz_loader.config
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def get_available_files() -> Dict:
    """
    사용 가능한 JSON 파일 목록

    Returns:
        JSON 파일 목록 및 현재 파일
    """
    try:
        files = quiz_loader.get_available_json_files()
        current_file = quiz_loader.current_filename

        return {
            "success": True,
            "files": files,
            "current_file": current_file
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-file")
async def load_file(filename: str) -> Dict:
    """
    특정 JSON 파일 로드

    Args:
        filename: 로드할 파일명 (확장자 제외)

    Returns:
        성공 여부 및 로드된 데이터 정보
    """
    try:
        filename = _sanitize_filename(filename)
        if not filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        quiz_loader.reload(filename)

        # 언어 자동 감지
        detected_languages = quiz_loader.detect_quiz_languages()

        return {
            "success": True,
            "message": f"File '{filename}' loaded successfully",
            "current_file": quiz_loader.current_filename,
            "detected_languages": detected_languages,
            "stats": {
                "quiz_items": len(quiz_loader.quiz_data),
                "available_images": len(quiz_loader.available_images),
                "config": quiz_loader.config
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats() -> Dict:
    """
    현재 퀴즈 데이터 통계

    Returns:
        퀴즈 아이템 수, 이미지 수, 설정 정보
    """
    return {
        "success": True,
        "stats": {
            "quiz_items": len(quiz_loader.quiz_data),
            "available_images": len(quiz_loader.available_images),
            "images": list(quiz_loader.available_images),
            "config": quiz_loader.config
        }
    }


@router.post("/check-answer")
async def check_answer(req: CheckAnswerRequest) -> Dict:
    """답안 확인 (주관식용)"""
    try:
        user_answer = req.user_answer.strip()
        correct_answer = req.correct_answer.strip()

        if not user_answer or not correct_answer:
            return {
                "success": False,
                "is_correct": False,
                "correct_answer": correct_answer,
                "message": "답변이 비어있습니다."
            }

        normalized_user = normalize_answer(user_answer)

        # 여러 정답이 있을 수 있음 (슬래시로 구분)
        correct_answers = [normalize_answer(ans.strip()) for ans in correct_answer.split('/')]

        is_correct = normalized_user in correct_answers

        return {
            "success": True,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "user_answer": user_answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-wrong-answer")
async def save_wrong_answer(req: SaveWrongAnswerRequest) -> Dict:
    """오답을 별도 파일로 저장"""
    try:
        current_filename = _sanitize_filename(
            getattr(quiz_loader, 'current_filename', 'quiz')
        )
        wrong_filename = f"{current_filename}_wrong.json"
        wrong_file_path = _get_data_dir() / wrong_filename

        # 기존 오답 파일 로드 또는 새로 생성
        if wrong_file_path.exists():
            with open(wrong_file_path, 'r', encoding='utf-8') as f:
                wrong_data = json.load(f)
        else:
            wrong_data = {}

        category = req.category
        if category not in wrong_data:
            wrong_data[category] = {}

        wrong_data[category][req.question] = req.answer

        with open(wrong_file_path, 'w', encoding='utf-8') as f:
            json.dump(wrong_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": f"Wrong answer saved to {wrong_filename}",
            "filename": wrong_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/find-images")
async def find_images(text: str) -> Dict:
    """
    주어진 텍스트와 일치하는 이미지 파일 찾기

    Args:
        text: 검색할 텍스트 (문제 또는 답)

    Returns:
        발견된 이미지 파일 경로 목록
    """
    try:
        img_dir = _get_data_dir() / "img"

        if not img_dir.exists():
            return {
                "success": True,
                "images": [],
                "message": "이미지 폴더가 없습니다."
            }

        # 이미지 확장자 목록
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}

        # 텍스트와 일치하는 이미지 파일 찾기
        found_images = []

        for img_file in img_dir.iterdir():
            if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                # 파일명 (확장자 제외)
                filename_without_ext = img_file.stem

                # 텍스트와 파일명이 일치하는지 확인
                if filename_without_ext.lower() == text.lower():
                    # 상대 경로로 변환
                    relative_path = f"/data/img/{img_file.name}"
                    found_images.append(relative_path)

        return {
            "success": True,
            "images": found_images,
            "count": len(found_images)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 학습 진도 저장/복원 ============

def _get_progress_file() -> Path:
    return _get_data_dir() / "progress.json"


@router.get("/progress")
async def get_progress() -> Dict:
    """학습 진도 조회"""
    try:
        progress_file = _get_progress_file()
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
            return {"success": True, "progress": progress}
        return {"success": True, "progress": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress")
async def save_progress(data: ProgressData) -> Dict:
    """학습 진도 저장"""
    try:
        progress = data.model_dump()
        progress["quiz_file"] = quiz_loader.current_filename
        progress["current_index"] = quiz_loader.current_index
        with open(_get_progress_file(), 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        return {"success": True, "message": "Progress saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 오답 복습 모드 ============

@router.get("/wrong-answers")
async def get_wrong_answers() -> Dict:
    """현재 퀴즈 파일의 오답 목록 조회"""
    try:
        current_filename = _sanitize_filename(
            getattr(quiz_loader, 'current_filename', 'quiz')
        )
        wrong_file_path = _get_data_dir() / f"{current_filename}_wrong.json"

        if not wrong_file_path.exists():
            return {"success": True, "wrong_answers": {}, "count": 0}

        with open(wrong_file_path, 'r', encoding='utf-8') as f:
            wrong_data = json.load(f)

        total = sum(len(items) for items in wrong_data.values())
        return {"success": True, "wrong_answers": wrong_data, "count": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review-wrong")
async def start_wrong_review() -> Dict:
    """오답 복습 모드 시작 - 오답 데이터를 문제 풀로 로드"""
    try:
        current_filename = _sanitize_filename(
            getattr(quiz_loader, 'current_filename', 'quiz')
        )
        wrong_file_path = _get_data_dir() / f"{current_filename}_wrong.json"

        if not wrong_file_path.exists():
            return {"success": False, "message": "오답 데이터가 없습니다."}

        with open(wrong_file_path, 'r', encoding='utf-8') as f:
            wrong_data = json.load(f)

        if not wrong_data:
            return {"success": False, "message": "오답 데이터가 비어있습니다."}

        # 오답 데이터를 quiz_loader에 임시로 로드
        quiz_loader.quiz_data = wrong_data
        quiz_loader.use_categories = True
        quiz_loader.rebuild_question_pool()

        total = sum(len(items) for items in wrong_data.values())
        return {
            "success": True,
            "message": f"오답 {total}개로 복습 모드를 시작합니다.",
            "count": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 누적 통계 ============

def _get_stats_file() -> Path:
    return _get_data_dir() / "session_stats.json"


@router.get("/session-stats")
async def get_session_stats() -> Dict:
    """누적 세션 통계 조회"""
    try:
        stats_file = _get_stats_file()
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                all_stats = json.load(f)
            return {"success": True, "stats": all_stats}
        return {"success": True, "stats": {"sessions": [], "total_questions": 0, "total_correct": 0}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session-stats")
async def save_session_stats(data: SessionStats) -> Dict:
    """세션 통계 저장 (최근 50개 세션만 유지)"""
    try:
        stats_file = _get_stats_file()
        existing = {"sessions": [], "total_questions": 0, "total_correct": 0}
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)

        session_data = data.model_dump()
        existing["sessions"].append(session_data)
        existing["total_questions"] += data.total
        existing["total_correct"] += data.correct

        # 최근 50개 세션만 유지
        if len(existing["sessions"]) > 50:
            existing["sessions"] = existing["sessions"][-50:]

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return {"success": True, "message": "Session stats saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
