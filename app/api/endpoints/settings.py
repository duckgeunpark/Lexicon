from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, List
from ...utils.data_loader import quiz_loader
import json
from pathlib import Path

router = APIRouter()


@router.get("/")
async def get_settings() -> Dict:
    """
    현재 설정 가져오기

    Returns:
        config.json 내용
    """
    return {
        "success": True,
        "settings": quiz_loader.config
    }


@router.post("/")
async def update_settings(settings: Dict) -> Dict:
    """
    설정 업데이트

    Args:
        settings: 새로운 설정 값

    Returns:
        업데이트 성공 여부
    """
    try:
        # 기존 quiz_file 값 저장
        old_quiz_file = quiz_loader.config.get("quiz_file", "quiz")
        new_quiz_file = settings.get("quiz_file", old_quiz_file)

        # 기존 config.json 읽기 (LLM 설정 보존용)
        config_path = Path("data/config.json")
        existing_config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        # 새로운 설정으로 업데이트 (LLM 설정은 유지)
        updated_config = {**settings}

        # LLM 관련 설정 보존
        if "llm" in existing_config:
            updated_config["llm"] = existing_config["llm"]
        if "llm_prompts" in existing_config:
            updated_config["llm_prompts"] = existing_config["llm_prompts"]

        # TTS 관련 설정 보존
        if "tts" in existing_config:
            updated_config["tts"] = existing_config["tts"]

        # 폰트 관련 설정 보존
        if "fonts" in existing_config:
            updated_config["fonts"] = existing_config["fonts"]

        # 시스템 관련 설정 보존
        if "system" in existing_config:
            updated_config["system"] = existing_config["system"]

        # 설정 파일 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(updated_config, f, ensure_ascii=False, indent=2)

        # 메모리에 로드
        quiz_loader.config = updated_config

        # 퀴즈 파일이 변경되었으면 새 파일 로드
        if new_quiz_file != old_quiz_file:
            quiz_loader.load_quiz_data(new_quiz_file)
            quiz_loader.scan_images()

        # 문제 풀 재구성 (카테고리나 순서 변경 시 필요)
        quiz_loader.rebuild_question_pool()

        return {
            "success": True,
            "message": "Settings updated successfully",
            "settings": settings,
            "current_file": quiz_loader.current_filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_available_languages() -> Dict:
    """
    사용 가능한 언어 목록

    Returns:
        지원 언어 목록
    """
    return {
        "success": True,
        "languages": {
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
            "zh": "中文",
            "es": "Español",
            "fr": "Français"
        }
    }


@router.get("/categories")
async def get_categories() -> Dict:
    """
    현재 로드된 퀴즈 데이터의 카테고리 목록

    Returns:
        카테고리 목록
    """
    try:
        categories = list(quiz_loader.quiz_data.keys())
        # 'default' 카테고리는 제외
        categories = [cat for cat in categories if cat != "default"]

        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tts")
async def get_tts_config() -> Dict:
    """
    TTS 설정 가져오기

    Returns:
        TTS 설정
    """
    config_path = Path("data/config.json")
    tts_config = {
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 1.0,
        "minNeonDuration": 500
    }

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if "tts" in config:
                tts_config = config["tts"]

    return {
        "success": True,
        "tts": tts_config
    }


@router.post("/tts")
async def update_tts_config(tts_config: Dict) -> Dict:
    """
    TTS 설정 업데이트

    Args:
        tts_config: TTS 설정 값

    Returns:
        업데이트 성공 여부
    """
    try:
        config_path = Path("data/config.json")

        # 기존 설정 읽기
        existing_config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        # TTS 설정 업데이트
        existing_config["tts"] = tts_config

        # 파일 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": "TTS config updated successfully",
            "tts": tts_config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fonts")
async def get_font_config() -> Dict:
    """
    폰트 설정 가져오기

    Returns:
        폰트 설정
    """
    config_path = Path("data/config.json")
    font_config = {
        "categorySize": 18,
        "questionSize": 64,
        "answerSize": 20,
        "fontFamily": "system-ui"
    }

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if "fonts" in config:
                font_config = config["fonts"]

    return {
        "success": True,
        "fonts": font_config
    }


@router.post("/fonts")
async def update_font_config(font_config: Dict) -> Dict:
    """
    폰트 설정 업데이트

    Args:
        font_config: 폰트 설정 값

    Returns:
        업데이트 성공 여부
    """
    try:
        config_path = Path("data/config.json")

        # 기존 설정 읽기
        existing_config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        # 폰트 설정 업데이트
        existing_config["fonts"] = font_config

        # 파일 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": "Font config updated successfully",
            "fonts": font_config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system")
async def get_system_config() -> Dict:
    """
    시스템 설정 가져오기

    Returns:
        시스템 설정 (다음 문제 딜레이, 단축키 등)
    """
    config_path = Path("data/config.json")
    system_config = {
        "nextQuestionDelay": 1500,
        "shortcuts": {
            "tts": "S",
            "llm": "L",
            "reload": "R",
            "settings": ",",
            "exit": "Escape"
        }
    }

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if "system" in config:
                system_config = config["system"]

    return {
        "success": True,
        "system": system_config
    }


@router.post("/system")
async def update_system_config(system_config: Dict) -> Dict:
    """
    시스템 설정 업데이트

    Args:
        system_config: 시스템 설정 값 (다음 문제 딜레이, 단축키 등)

    Returns:
        업데이트 성공 여부
    """
    try:
        config_path = Path("data/config.json")

        # 기존 설정 읽기
        existing_config = {}
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        # 시스템 설정 업데이트
        existing_config["system"] = system_config

        # 파일 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "message": "System config updated successfully",
            "system": system_config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-quiz")
async def upload_quiz_file(file: UploadFile = File(...)) -> Dict:
    """
    퀴즈 JSON 파일 업로드

    Args:
        file: 업로드할 JSON 파일

    Returns:
        성공 여부 및 파일 정보
    """
    try:
        # 파일 내용 읽기
        contents = await file.read()
        quiz_data = json.loads(contents.decode('utf-8'))

        # 임시로 메모리에 로드
        quiz_loader.quiz_data = {}

        # 카테고리 구조 감지
        if quiz_data and isinstance(next(iter(quiz_data.values()), None), dict):
            quiz_loader.quiz_data = quiz_data
            quiz_loader.use_categories = True
        else:
            quiz_loader.quiz_data = {"default": quiz_data}
            quiz_loader.use_categories = False

        # 선택된 카테고리 초기화 (모두 선택)
        if not hasattr(quiz_loader.config, 'selected_categories'):
            quiz_loader.config['selected_categories'] = list(quiz_loader.quiz_data.keys())

        # 문제 풀 재구성 (중요!)
        quiz_loader.rebuild_question_pool()

        return {
            "success": True,
            "filename": file.filename,
            "categories": list(quiz_loader.quiz_data.keys()),
            "item_count": sum(len(items) for items in quiz_loader.quiz_data.values())
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
