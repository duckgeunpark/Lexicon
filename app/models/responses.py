"""
API 응답 모델
"""
from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class BaseResponse(BaseModel):
    success: bool = True
    message: str = ""


class QuestionOption(BaseModel):
    id: str
    text: str
    is_correct: bool


class QuestionResponse(BaseModel):
    success: bool = True
    data: Optional[Dict[str, Any]] = None


class CheckAnswerResponse(BaseModel):
    success: bool
    is_correct: bool = False
    correct_answer: str = ""
    user_answer: str = ""
    message: str = ""


class StatsResponse(BaseModel):
    success: bool = True
    stats: Dict[str, Any] = {}


class FilesResponse(BaseModel):
    success: bool = True
    files: List[str] = []
    current_file: str = ""


# ============ LLM 응답 모델 ============

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


class LLMChatResponse(BaseModel):
    """LLM 채팅 응답 모델"""
    success: bool
    response: str
    error: str = ""


class PersonaInfo(BaseModel):
    """페르소나 정보 모델"""
    name: str
    description: str
