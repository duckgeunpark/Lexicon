"""
LLM 프롬프트 관리
"""
from typing import Dict, Any


class PromptManager:
    """프롬프트 관리 클래스"""

    DEFAULT_SYSTEM_PROMPT = "친절한 언어 학습 도우미. 명확한 설명, 예문, 발음 가이드 제공. 학습자 수준에 맞춰 격려하며 답변."

    DEFAULT_PERSONA = "friendly_tutor"

    PERSONAS = {
        "friendly_tutor": {
            "name": "친절한 튜터",
            "description": "친근하고 격려적인 언어 학습 도우미",
            "system_prompt": DEFAULT_SYSTEM_PROMPT
        },
        "professional_teacher": {
            "name": "전문 교사",
            "description": "체계적이고 상세한 설명을 제공하는 교사",
            "system_prompt": "언어 교육 전문가. 체계적 문법 설명, 언어학적 배경, 유사 표현 비교. 구조화된 형식, 정확한 용어 사용."
        },
        "casual_friend": {
            "name": "친구 같은 도우미",
            "description": "편안하고 일상적인 대화로 돕는 친구",
            "system_prompt": "편안한 친구처럼 대화하는 언어 도우미. 일상 표현 중심, 재미있는 예시, 부담 없이 격려."
        },
        "native_speaker": {
            "name": "원어민 화자",
            "description": "원어민 관점에서 자연스러운 표현을 알려주는 도우미",
            "system_prompt": "원어민 화자 역할. 실제 사용 표현, 교과서와의 차이, 문화적 뉘앙스, 지역/세대별 차이 설명."
        },
        "grammar_expert": {
            "name": "문법 전문가",
            "description": "문법 규칙과 구조를 상세히 설명하는 전문가",
            "system_prompt": "문법 전문가. 규칙/구조 분석, 품사/시제/어순, 예외 케이스. 체계적 설명, 정확한 용어."
        }
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: LLM 프롬프트 설정 딕셔너리
        """
        self.config = config

    def get_system_prompt(self) -> str:
        """시스템 프롬프트 가져오기"""
        # 커스텀 시스템 프롬프트가 있으면 사용
        if self.config.get("custom_system_prompt"):
            return self.config["custom_system_prompt"]

        # 페르소나 기반 프롬프트
        persona = self.config.get("persona", self.DEFAULT_PERSONA)
        if persona in self.PERSONAS:
            return self.PERSONAS[persona]["system_prompt"]

        # 기본 프롬프트
        return self.DEFAULT_SYSTEM_PROMPT

    def build_messages(self, user_question: str, context: Dict[str, Any] = None) -> list[Dict[str, str]]:
        """대화 메시지 구성"""
        messages = []

        # 시스템 프롬프트
        system_prompt = self.get_system_prompt()

        # 컨텍스트 추가 (현재 문제 정보 등)
        if context:
            context_info = self._format_context(context)
            if context_info:
                system_prompt += f"\n\n[참고 컨텍스트 - 사용자가 현재 학습 중인 내용입니다. 사용자의 질문과 관련될 때만 참고하세요.]\n{context_info}"

        system_prompt += "\n\n중요 규칙:\n1. 반드시 사용자의 실제 질문에 직접 답변하세요. 컨텍스트 정보는 질문과 관련될 때만 참고하고, 질문과 무관하면 무시하세요.\n2. 답변은 간결하고 핵심 위주로 작성하세요. 불필요하게 길거나 장황한 답변은 피하세요."

        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # 사용자 질문
        messages.append({
            "role": "user",
            "content": user_question
        })

        return messages

    def _format_context(self, context: Dict[str, Any]) -> str:
        """컨텍스트 정보 포맷팅"""
        parts = []

        if context.get("category"):
            parts.append(f"주제: {context['category']}")

        if context.get("question"):
            parts.append(f"현재 문제: {context['question']}")

        if context.get("answer"):
            parts.append(f"정답: {context['answer']}")

        if context.get("language_pair"):
            lang1, lang2 = context["language_pair"]
            parts.append(f"학습 언어: {lang1} ↔ {lang2}")

        return "\n".join(parts) if parts else ""

    @classmethod
    def get_available_personas(cls) -> Dict[str, Dict[str, str]]:
        """사용 가능한 페르소나 목록"""
        return {
            key: {"name": value["name"], "description": value["description"]}
            for key, value in cls.PERSONAS.items()
        }
