"""
LLM 설정 및 채팅 API 엔드포인트
"""
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.llm import LLMService

router = APIRouter()

# config.json 파일 경로
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "data" / "config.json"

# LLM 서비스 인스턴스
llm_service = LLMService(CONFIG_FILE)


# ============ 모델 정의 ============

class LLMConfig(BaseModel):
    """LLM 기본 설정 모델"""
    llm_model: str
    api_key: str


class LLMPromptConfig(BaseModel):
    """LLM 프롬프트 설정 모델"""
    persona: str
    custom_system_prompt: Optional[str] = ""
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024


class LLMFullConfig(BaseModel):
    """LLM 전체 설정 모델"""
    llm_model: str
    api_key: str
    prompts: LLMPromptConfig


class LLMConfigResponse(BaseModel):
    """LLM 설정 응답 모델"""
    llm_model: str = ""
    api_key: str = ""
    prompts: Dict[str, Any] = {}
    has_config: bool = False


class LLMTestResponse(BaseModel):
    """LLM 연결 테스트 응답 모델"""
    success: bool
    status: str  # "connected", "warning", "disconnected"
    message: str


class LLMChatRequest(BaseModel):
    """LLM 채팅 요청 모델"""
    question: str
    context: Optional[Dict[str, Any]] = None


class LLMChatResponse(BaseModel):
    """LLM 채팅 응답 모델"""
    success: bool
    response: str
    error: str = ""


class PersonaInfo(BaseModel):
    """페르소나 정보 모델"""
    name: str
    description: str


# ============ 엔드포인트 ============

@router.get("/config", response_model=LLMConfigResponse)
async def get_llm_config():
    """LLM 설정 조회"""
    try:
        config = llm_service.get_config()

        return LLMConfigResponse(
            llm_model=config.get("model", ""),
            api_key=config.get("api_key", ""),
            prompts=config.get("prompts", {}),
            has_config=config.get("has_config", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 로드 실패: {str(e)}")


@router.post("/config")
async def save_llm_config(config: LLMConfig):
    """LLM 기본 설정 저장 (모델, API 키만)"""
    try:
        llm_service.save_config(
            model=config.llm_model,
            api_key=config.api_key
        )

        return {"success": True, "message": "LLM 설정이 저장되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 저장 실패: {str(e)}")


@router.post("/config/full")
async def save_llm_full_config(config: LLMFullConfig):
    """LLM 전체 설정 저장 (모델, API 키, 프롬프트)"""
    try:
        prompts_dict = {
            "persona": config.prompts.persona,
            "custom_system_prompt": config.prompts.custom_system_prompt or "",
            "temperature": config.prompts.temperature,
            "max_tokens": config.prompts.max_tokens
        }

        llm_service.save_config(
            model=config.llm_model,
            api_key=config.api_key,
            prompts=prompts_dict
        )

        return {"success": True, "message": "LLM 설정이 저장되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"설정 저장 실패: {str(e)}")


@router.post("/prompts")
async def save_llm_prompts(prompts: LLMPromptConfig):
    """LLM 프롬프트 설정만 저장"""
    try:
        # 기존 설정 로드
        config = llm_service.get_config()

        prompts_dict = {
            "persona": prompts.persona,
            "custom_system_prompt": prompts.custom_system_prompt or "",
            "temperature": prompts.temperature,
            "max_tokens": prompts.max_tokens
        }

        # 기존 모델/API 키와 함께 저장
        llm_service.save_config(
            model=config.get("model", ""),
            api_key=config.get("api_key", ""),
            prompts=prompts_dict
        )

        return {"success": True, "message": "프롬프트 설정이 저장되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프롬프트 설정 저장 실패: {str(e)}")


@router.get("/personas")
async def get_available_personas():
    """사용 가능한 페르소나 목록 조회"""
    try:
        personas = LLMService.get_available_personas()
        return {
            "success": True,
            "personas": personas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"페르소나 조회 실패: {str(e)}")


@router.post("/test", response_model=LLMTestResponse)
async def test_llm_connection():
    """LLM 연결 테스트"""
    try:
        success, message = await llm_service.test_connection()

        if success:
            status = "connected"
        elif "유효하지 않" in message or "찾을 수 없" in message:
            status = "disconnected"
        else:
            status = "warning"

        return LLMTestResponse(
            success=success,
            status=status,
            message=message
        )
    except Exception as e:
        return LLMTestResponse(
            success=False,
            status="warning",
            message=f"연결 테스트 실패: {str(e)}"
        )


@router.post("/chat", response_model=LLMChatResponse)
async def llm_chat(request: LLMChatRequest):
    """LLM에게 질문하고 답변 받기"""
    try:
        # LLM 호출
        response = await llm_service.chat(
            question=request.question,
            context=request.context
        )

        return LLMChatResponse(
            success=True,
            response=response,
            error=""
        )

    except FileNotFoundError:
        return LLMChatResponse(
            success=False,
            response="",
            error="LLM 설정이 없습니다. 먼저 LLM 설정을 완료해주세요."
        )
    except ValueError as e:
        return LLMChatResponse(
            success=False,
            response="",
            error=str(e)
        )
    except Exception as e:
        return LLMChatResponse(
            success=False,
            response="",
            error=f"LLM 요청 실패: {str(e)}"
        )
