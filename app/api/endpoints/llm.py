"""
LLM 설정 및 채팅 API 엔드포인트
"""
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict

from app.llm import LLMService
from ...models.requests import (
    LLMConfig, LLMPromptConfig, LLMFullConfig, LLMChatRequest
)
from ...models.responses import (
    LLMConfigResponse, LLMTestResponse, LLMChatResponse
)

router = APIRouter()

# config.json 파일 경로 (빌드 환경 대응)
from ...core import paths as app_paths
CONFIG_FILE = app_paths.get_config_path()

# LLM 서비스 인스턴스
llm_service = LLMService(CONFIG_FILE)


def _mask_api_key(key: str) -> str:
    """API 키를 마스킹하여 반환 (앞 4자, 뒤 4자만 노출)"""
    if not key or len(key) <= 8:
        return "****" if key else ""
    return f"{key[:4]}...{key[-4:]}"


# ============ 엔드포인트 ============

@router.get("/config", response_model=LLMConfigResponse)
async def get_llm_config():
    """LLM 설정 조회"""
    try:
        config = llm_service.get_config()

        return LLMConfigResponse(
            llm_model=config.get("model", ""),
            api_key=_mask_api_key(config.get("api_key", "")),
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


@router.post("/chat/stream")
async def llm_chat_stream(request: LLMChatRequest):
    """LLM 스트리밍 채팅 (SSE)"""
    async def event_generator():
        try:
            async for chunk in llm_service.chat_stream(
                question=request.question,
                context=request.context
            ):
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
