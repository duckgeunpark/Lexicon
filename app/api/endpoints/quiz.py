from fastapi import APIRouter, HTTPException
from typing import Dict
from ...utils.data_loader import quiz_loader
import json
from pathlib import Path

router = APIRouter()


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
async def check_answer(answer_data: Dict) -> Dict:
    """
    답안 확인 (주관식용)

    Args:
        answer_data: {
            "user_answer": 사용자 답변,
            "correct_answer": 정답,
            "question": 문제 (선택),
            "category": 카테고리 (선택)
        }

    Returns:
        정답 여부 및 정답
    """
    try:
        user_answer = answer_data.get("user_answer", "").strip()
        correct_answer = answer_data.get("correct_answer", "").strip()

        if not user_answer or not correct_answer:
            return {
                "success": False,
                "is_correct": False,
                "correct_answer": correct_answer,
                "message": "답변이 비어있습니다."
            }

        # 📌 정답 체크 로직 (대소문자 무시, 공백 제거)
        def normalize_answer(text: str) -> str:
            """답안 정규화: 소문자 변환, 공백 제거, 특수문자 정리"""
            import re
            # 소문자 변환
            text = text.lower()
            # 앞뒤 공백 제거
            text = text.strip()
            # 연속된 공백을 하나로
            text = re.sub(r'\s+', ' ', text)
            return text

        normalized_user = normalize_answer(user_answer)
        normalized_correct = normalize_answer(correct_answer)

        # 📌 여러 정답이 있을 수 있음 (슬래시로 구분)
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
async def save_wrong_answer(wrong_item: Dict) -> Dict:
    """
    오답을 별도 파일로 저장

    Args:
        wrong_item: 오답 항목 (category, question, answer)

    Returns:
        저장 성공 여부
    """
    try:
        # 현재 파일명 가져오기
        current_filename = getattr(quiz_loader, 'current_filename', 'quiz')
        wrong_filename = f"{current_filename}_wrong.json"
        wrong_file_path = Path("data") / wrong_filename

        # 기존 오답 파일 로드 또는 새로 생성
        if wrong_file_path.exists():
            with open(wrong_file_path, 'r', encoding='utf-8') as f:
                wrong_data = json.load(f)
        else:
            wrong_data = {}

        # 카테고리별로 저장
        category = wrong_item.get('category', 'default')
        question = wrong_item.get('question')
        answer = wrong_item.get('answer')

        if category not in wrong_data:
            wrong_data[category] = {}

        wrong_data[category][question] = answer

        # 파일 저장
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
        img_dir = Path("data") / "img"

        if not img_dir.exists():
            return {
                "success": True,
                "images": [],
                "message": "이미지 폴더가 없습니다."
            }

        # 이미지 확장자 목록
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']

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
