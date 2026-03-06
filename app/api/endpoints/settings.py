import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict
from ...utils.data_loader import quiz_loader
from ...core.config import ConfigManager
from ...models.requests import TTSConfig, FontConfig, SystemConfig

router = APIRouter()

_PRESERVE_SECTIONS = ["llm", "llm_prompts", "tts", "fonts", "system"]

_DEFAULT_TTS = {
    "rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0,
    "minNeonDuration": 500
}

_DEFAULT_FONTS = {
    "categorySize": 18,
    "questionSize": 64,
    "answerSize": 20,
    "fontFamily": "system-ui"
}

_DEFAULT_SYSTEM = {
    "nextQuestionDelay": 1500,
    "shortcuts": {
        "tts": "S",
        "llm": "L",
        "reload": "R",
        "settings": ",",
        "exit": "Escape"
    }
}


def _get_cfg() -> ConfigManager:
    return ConfigManager.get_instance()


@router.get("/")
async def get_settings() -> Dict:
    """현재 설정 가져오기"""
    return {
        "success": True,
        "settings": _get_cfg().get_all()
    }


@router.post("/")
async def update_settings(settings: Dict) -> Dict:
    """설정 업데이트"""
    try:
        cfg = _get_cfg()
        old_quiz_file = cfg.get("quiz_file", "quiz")
        new_quiz_file = settings.get("quiz_file", old_quiz_file)

        old_categories = cfg.get("selected_categories", [])
        old_order = cfg.get("order_mode", "random")

        # 설정 교체 (LLM, TTS, 폰트, 시스템 섹션 보존)
        cfg.replace(settings, preserve_sections=_PRESERVE_SECTIONS)

        # ConfigManager를 통해 메모리에 반영
        quiz_loader.load_config()

        # 퀴즈 파일이 변경되었으면 새 파일 로드
        need_rebuild = False
        if new_quiz_file != old_quiz_file:
            quiz_loader.load_quiz_data(new_quiz_file)
            quiz_loader.scan_images()
            need_rebuild = True

        # 카테고리나 순서가 변경된 경우에만 풀 재구성
        new_categories = settings.get("selected_categories", old_categories)
        new_order = settings.get("order_mode", old_order)
        if need_rebuild or new_categories != old_categories or new_order != old_order:
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
    """사용 가능한 언어 목록"""
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
    """현재 로드된 퀴즈 데이터의 카테고리 목록"""
    try:
        categories = [cat for cat in quiz_loader.quiz_data.keys() if cat != "default"]
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tts")
async def get_tts_config() -> Dict:
    """TTS 설정 가져오기"""
    tts_config = _get_cfg().get_section("tts") or _DEFAULT_TTS
    return {"success": True, "tts": tts_config}


@router.post("/tts")
async def update_tts_config(tts_config: TTSConfig) -> Dict:
    """TTS 설정 업데이트"""
    try:
        data = tts_config.model_dump()
        _get_cfg().set_section("tts", data)
        return {
            "success": True,
            "message": "TTS config updated successfully",
            "tts": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fonts")
async def get_font_config() -> Dict:
    """폰트 설정 가져오기"""
    font_config = _get_cfg().get_section("fonts") or _DEFAULT_FONTS
    return {"success": True, "fonts": font_config}


@router.post("/fonts")
async def update_font_config(font_config: FontConfig) -> Dict:
    """폰트 설정 업데이트"""
    try:
        data = font_config.model_dump()
        _get_cfg().set_section("fonts", data)
        return {
            "success": True,
            "message": "Font config updated successfully",
            "fonts": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system")
async def get_system_config() -> Dict:
    """시스템 설정 가져오기"""
    system_config = _get_cfg().get_section("system") or _DEFAULT_SYSTEM
    return {"success": True, "system": system_config}


@router.post("/system")
async def update_system_config(system_config: SystemConfig) -> Dict:
    """시스템 설정 업데이트"""
    try:
        data = system_config.model_dump()
        _get_cfg().set_section("system", data)
        return {
            "success": True,
            "message": "System config updated successfully",
            "system": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-quiz")
async def upload_quiz_file(file: UploadFile = File(...)) -> Dict:
    """퀴즈 JSON 파일 업로드"""
    try:
        contents = await file.read()
        quiz_data = json.loads(contents.decode('utf-8'))

        quiz_loader.quiz_data = {}

        if quiz_data and isinstance(next(iter(quiz_data.values()), None), dict):
            quiz_loader.quiz_data = quiz_data
            quiz_loader.use_categories = True
        else:
            quiz_loader.quiz_data = {"default": quiz_data}
            quiz_loader.use_categories = False

        if 'selected_categories' not in quiz_loader.config:
            quiz_loader.config['selected_categories'] = list(quiz_loader.quiz_data.keys())

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
