"""
LLM 서비스 클래스
"""
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
from .providers import get_provider, LLMProvider
from .prompts import PromptManager


class LLMService:
    """LLM 통합 서비스"""

    def __init__(self, config_path: Path = None):
        """
        Args:
            config_path: config.json 파일 경로
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "data" / "config.json"

        self.config_path = config_path
        self._provider: Optional[LLMProvider] = None
        self._prompt_manager: Optional[PromptManager] = None

    def _load_config(self) -> Dict[str, Any]:
        """설정 로드"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_provider(self) -> LLMProvider:
        """LLM 제공자 가져오기 (캐시됨)"""
        if self._provider is None:
            config = self._load_config()
            llm_config = config.get("llm", {})
            llm_prompts = config.get("llm_prompts", {})

            model = llm_config.get("model")
            api_key = llm_config.get("api_key")
            temperature = llm_prompts.get("temperature", 0.7)
            max_tokens = llm_prompts.get("max_tokens", 1024)

            if not model or not api_key:
                raise ValueError("LLM 모델 또는 API 키가 설정되지 않았습니다")

            self._provider = get_provider(model, api_key, temperature, max_tokens)

        return self._provider

    def _get_prompt_manager(self) -> PromptManager:
        """프롬프트 매니저 가져오기 (캐시됨)"""
        if self._prompt_manager is None:
            config = self._load_config()
            llm_prompts = config.get("llm_prompts", {})
            self._prompt_manager = PromptManager(llm_prompts)

        return self._prompt_manager

    def reset_cache(self):
        """캐시 초기화 (설정 변경 시 호출)"""
        self._provider = None
        self._prompt_manager = None

    async def chat(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        사용자 질문에 대한 LLM 응답 생성

        Args:
            question: 사용자 질문
            context: 추가 컨텍스트 (현재 문제 정보 등)

        Returns:
            LLM 응답 텍스트
        """
        provider = self._get_provider()
        prompt_manager = self._get_prompt_manager()

        # 메시지 구성
        messages = prompt_manager.build_messages(question, context)

        # LLM 호출
        response = await provider.chat(messages)

        return response

    async def test_connection(self) -> Tuple[bool, str]:
        """
        LLM 연결 테스트

        Returns:
            (성공 여부, 메시지)
        """
        try:
            provider = self._get_provider()
            success, message = await provider.test_connection()
            return success, message
        except FileNotFoundError:
            return False, "설정 파일을 찾을 수 없습니다"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"연결 테스트 실패: {str(e)}"

    def get_config(self) -> Dict[str, Any]:
        """현재 LLM 설정 가져오기"""
        try:
            config = self._load_config()
            llm_config = config.get("llm", {})
            llm_prompts = config.get("llm_prompts", {})

            return {
                "model": llm_config.get("model", ""),
                "api_key": llm_config.get("api_key", ""),
                "prompts": llm_prompts,
                "has_config": bool(llm_config.get("model") and llm_config.get("api_key"))
            }
        except FileNotFoundError:
            return {
                "model": "",
                "api_key": "",
                "prompts": {},
                "has_config": False
            }

    def save_config(self, model: str, api_key: str, prompts: Dict[str, Any] = None):
        """
        LLM 설정 저장

        Args:
            model: LLM 모델명
            api_key: API 키
            prompts: 프롬프트 설정 (선택)
        """
        # 기존 설정 로드
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {}

        # LLM 기본 설정 업데이트
        config["llm"] = {
            "model": model,
            "api_key": api_key
        }

        # 프롬프트 설정 업데이트
        if prompts is not None:
            config["llm_prompts"] = prompts

        # 파일 저장
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        # 캐시 초기화
        self.reset_cache()

    @staticmethod
    def get_available_personas() -> Dict[str, Dict[str, str]]:
        """사용 가능한 페르소나 목록"""
        return PromptManager.get_available_personas()
