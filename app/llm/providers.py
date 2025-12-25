"""
LLM 제공자별 구현
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
import json


class LLMProvider(ABC):
    """LLM 제공자 추상 클래스"""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 1024):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def chat(self, messages: list[Dict[str, str]]) -> str:
        """채팅 요청"""
        pass

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str]:
        """연결 테스트"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API 제공자"""

    BASE_URL = "https://api.openai.com/v1/chat/completions"

    async def chat(self, messages: list[Dict[str, str]]) -> str:
        """OpenAI 채팅 API 호출"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def test_connection(self) -> tuple[bool, str]:
        """OpenAI API 연결 테스트"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat(test_messages)
            return True, "OpenAI 연결 성공"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return False, "API 키가 유효하지 않습니다"
            return False, f"연결 실패: {e.response.status_code}"
        except Exception as e:
            return False, f"연결 실패: {str(e)}"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API 제공자"""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    async def chat(self, messages: list[Dict[str, str]]) -> str:
        """Anthropic 채팅 API 호출"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json"
        }

        # system 메시지 분리
        system_message = ""
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": user_messages
        }

        if system_message:
            payload["system"] = system_message

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]

    async def test_connection(self) -> tuple[bool, str]:
        """Anthropic API 연결 테스트"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat(test_messages)
            return True, "Anthropic 연결 성공"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return False, "API 키가 유효하지 않습니다"
            return False, f"연결 실패: {e.response.status_code}"
        except Exception as e:
            return False, f"연결 실패: {str(e)}"


class GoogleProvider(LLMProvider):
    """Google Gemini API 제공자"""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async def chat(self, messages: list[Dict[str, str]]) -> str:
        """Google Gemini API 호출"""
        url = self.BASE_URL.format(model=self.model)

        # Google API는 다른 형식 사용
        contents = []
        system_instruction = None

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        params = {"key": self.api_key}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def test_connection(self) -> tuple[bool, str]:
        """Google Gemini API 연결 테스트"""
        try:
            test_messages = [{"role": "user", "content": "Hello"}]
            await self.chat(test_messages)
            return True, "Google Gemini 연결 성공"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_data = e.response.json()
                if "API key not valid" in str(error_data):
                    return False, "API 키가 유효하지 않습니다"
            return False, f"연결 실패: {e.response.status_code}"
        except Exception as e:
            return False, f"연결 실패: {str(e)}"


def get_provider(model: str, api_key: str, temperature: float = 0.7, max_tokens: int = 1024) -> Optional[LLMProvider]:
    """모델명에 따라 적절한 제공자 반환"""
    model_lower = model.lower()

    # OpenAI 모델
    if any(x in model_lower for x in ["gpt-3", "gpt-4", "gpt-4-turbo"]):
        return OpenAIProvider(api_key, model, temperature, max_tokens)

    # Anthropic Claude 모델
    elif "claude" in model_lower:
        return AnthropicProvider(api_key, model, temperature, max_tokens)

    # Google Gemini 모델
    elif "gemini" in model_lower:
        return GoogleProvider(api_key, model, temperature, max_tokens)

    # 기본값: OpenAI로 시도
    return OpenAIProvider(api_key, model, temperature, max_tokens)
