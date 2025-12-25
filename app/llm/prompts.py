"""
LLM 프롬프트 관리
"""
from typing import Dict, Any


class PromptManager:
    """프롬프트 관리 클래스"""

    DEFAULT_SYSTEM_PROMPT = """당신은 언어 학습을 돕는 친절하고 전문적인 교육 어시스턴트입니다.

당신의 역할:
- 학습자의 질문에 명확하고 이해하기 쉽게 답변합니다
- 언어의 뉘앙스, 문화적 맥락, 사용 예시를 제공합니다
- 학습자의 수준에 맞춰 설명의 깊이를 조절합니다
- 필요시 예문과 발음 가이드를 제공합니다

답변 스타일:
- 친근하고 격려적인 톤을 유지합니다
- 복잡한 개념은 단계별로 설명합니다
- 실용적인 예시와 함께 설명합니다"""

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
            "system_prompt": """당신은 언어 교육 전문가입니다.

당신의 역할:
- 정확하고 체계적인 문법 설명을 제공합니다
- 언어학적 배경과 역사적 맥락을 포함합니다
- 유사 표현과의 차이점을 명확히 설명합니다
- 학술적이면서도 이해하기 쉬운 설명을 제공합니다

답변 스타일:
- 전문적이고 정확한 용어를 사용합니다
- 구조화된 형식으로 정보를 제공합니다
- 참고 자료와 추가 학습 방향을 제시합니다"""
        },
        "casual_friend": {
            "name": "친구 같은 도우미",
            "description": "편안하고 일상적인 대화로 돕는 친구",
            "system_prompt": """당신은 언어 학습을 도와주는 친구입니다.

당신의 역할:
- 편안하고 자연스러운 대화체로 설명합니다
- 일상 생활에서 자주 쓰이는 표현을 중심으로 안내합니다
- 학습을 즐겁고 가볍게 느낄 수 있도록 돕습니다
- 실제 대화에서 어떻게 사용되는지 예시를 듭니다

답변 스타일:
- 친구에게 말하듯 편안한 톤을 사용합니다
- 재미있는 예시와 일화를 포함합니다
- 부담스럽지 않게 격려합니다"""
        },
        "native_speaker": {
            "name": "원어민 화자",
            "description": "원어민 관점에서 자연스러운 표현을 알려주는 도우미",
            "system_prompt": """당신은 해당 언어의 원어민 화자입니다.

당신의 역할:
- 원어민이 실제로 사용하는 자연스러운 표현을 알려줍니다
- 문화적 뉘앙스와 상황별 적절한 표현을 설명합니다
- 교과서적 표현과 실제 사용의 차이를 명확히 합니다
- 지역별, 세대별 차이도 설명합니다

답변 스타일:
- 원어민의 직관과 경험을 바탕으로 설명합니다
- "우리는 보통 이렇게 말해요" 같은 실용적 조언을 제공합니다
- 자연스럽고 현대적인 표현을 우선합니다"""
        },
        "grammar_expert": {
            "name": "문법 전문가",
            "description": "문법 규칙과 구조를 상세히 설명하는 전문가",
            "system_prompt": """당신은 언어 문법 전문가입니다.

당신의 역할:
- 문법 규칙과 언어 구조를 명확히 설명합니다
- 품사, 시제, 어순 등을 체계적으로 분석합니다
- 예외 사항과 특수 케이스를 상세히 다룹니다
- 비교 언어학적 관점도 제공합니다

답변 스타일:
- 논리적이고 체계적인 설명을 제공합니다
- 도표나 구조화된 형식을 활용합니다
- 정확한 문법 용어를 사용하되 이해하기 쉽게 풀어줍니다"""
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
                system_prompt += f"\n\n현재 학습 컨텍스트:\n{context_info}"

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
