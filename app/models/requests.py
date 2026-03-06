"""
API 요청 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any


class TTSConfig(BaseModel):
    rate: float = Field(1.0, ge=0.1, le=2.0)
    pitch: float = Field(1.0, ge=0.5, le=2.0)
    volume: float = Field(1.0, ge=0.0, le=1.0)
    minNeonDuration: int = Field(500, ge=0, le=2000)


class FontConfig(BaseModel):
    fontFamily: str = "system-ui"
    categorySize: int = Field(18, ge=12, le=32)
    questionSize: int = Field(64, ge=24, le=120)
    answerSize: int = Field(20, ge=14, le=32)


class ShortcutsConfig(BaseModel):
    tts: str = "S"
    llm: str = "L"
    reload: str = "R"
    settings: str = ","
    exit: str = "Escape"


class SystemConfig(BaseModel):
    nextQuestionDelay: int = Field(1500, ge=0, le=5000)
    shortcuts: ShortcutsConfig = ShortcutsConfig()


class QuizSettingsUpdate(BaseModel):
    quiz_file: Optional[str] = None
    language1: Optional[str] = None
    language2: Optional[str] = None
    question_pattern: Optional[str] = None
    random_patterns: Optional[Dict[str, bool]] = None
    quiz_type: Optional[str] = None
    quiz_types: Optional[Dict[str, bool]] = None
    order_mode: Optional[str] = None
    selected_categories: Optional[List[str]] = None


class ProgressData(BaseModel):
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    current_index: int = 0
    quiz_file: Optional[str] = None


class SessionStats(BaseModel):
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    accuracy: float = 0.0
    duration_seconds: float = 0.0


# ============ Quiz 요청 모델 ============

class CheckAnswerRequest(BaseModel):
    user_answer: str
    correct_answer: str
    question: Optional[str] = None
    category: Optional[str] = None


class SaveWrongAnswerRequest(BaseModel):
    category: str = "default"
    question: str
    answer: str


# ============ LLM 요청 모델 ============

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


class LLMChatRequest(BaseModel):
    """LLM 채팅 요청 모델"""
    question: str
    context: Optional[Dict[str, Any]] = None
