"""
LLM 제공자별 구현 (공유 AsyncClient 사용)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
import httpx
import json
import asyncio


# 모듈 레벨 공유 클라이언트 (asyncio.Lock으로 race condition 방지)
_shared_client: Optional[httpx.AsyncClient] = None
_client_lock = asyncio.Lock()


async def get_shared_client() -> httpx.AsyncClient:
    """공유 httpx AsyncClient 반환 (thread-safe lazy init)"""
    global _shared_client
    async with _client_lock:
        if _shared_client is None or _shared_client.is_closed:
            _shared_client = httpx.AsyncClient(timeout=30.0)
    return _shared_client


async def close_shared_client():
    """서버 종료 시 공유 클라이언트 정리"""
    global _shared_client
    async with _client_lock:
        if _shared_client is not None and not _shared_client.is_closed:
            await _shared_client.aclose()
            _shared_client = None


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

    async def chat_stream(self, messages: list[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """스트리밍 채팅 (기본 구현은 non-streaming fallback)"""
        result = await self.chat(messages)
        yield result


class OpenAIProvider(LLMProvider):
    """OpenAI API 제공자"""

    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODELS_URL = "https://api.openai.com/v1/models"

    async def chat(self, messages: list[Dict[str, str]]) -> str:
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

        client = await get_shared_client()
        response = await client.post(self.BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list[Dict[str, str]]) -> AsyncGenerator[str, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True
        }
        client = await get_shared_client()
        async with client.stream("POST", self.BASE_URL, headers=headers, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk_data = line[6:]
                    if chunk_data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(chunk_data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue

    async def test_connection(self) -> tuple[bool, str]:
        """모델 목록 API로 경량 연결 테스트 (토큰 소비 없음)"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            client = await get_shared_client()
            response = await client.get(self.MODELS_URL, headers=headers)
            response.raise_for_status()
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

    def _build_payload(self, messages):
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
        return payload

    def _get_headers(self):
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json"
        }

    async def chat(self, messages: list[Dict[str, str]]) -> str:
        payload = self._build_payload(messages)
        client = await get_shared_client()
        response = await client.post(self.BASE_URL, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    async def chat_stream(self, messages: list[Dict[str, str]]) -> AsyncGenerator[str, None]:
        payload = self._build_payload(messages)
        payload["stream"] = True
        client = await get_shared_client()
        async with client.stream("POST", self.BASE_URL, headers=self._get_headers(), json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        chunk = json.loads(line[6:])
                        if chunk.get("type") == "content_block_delta":
                            text = chunk.get("delta", {}).get("text", "")
                            if text:
                                yield text
                    except json.JSONDecodeError:
                        continue

    async def test_connection(self) -> tuple[bool, str]:
        """최소 토큰으로 연결 테스트"""
        try:
            test_messages = [{"role": "user", "content": "Hi"}]
            payload = self._build_payload(test_messages)
            payload["max_tokens"] = 1  # 최소 토큰만 사용
            client = await get_shared_client()
            response = await client.post(self.BASE_URL, headers=self._get_headers(), json=payload)
            response.raise_for_status()
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
    STREAM_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"
    MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def _build_payload(self, messages):
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
        return payload

    async def chat(self, messages: list[Dict[str, str]]) -> str:
        url = self.BASE_URL.format(model=self.model)
        payload = self._build_payload(messages)
        params = {"key": self.api_key}

        client = await get_shared_client()
        response = await client.post(url, params=params, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def chat_stream(self, messages: list[Dict[str, str]]) -> AsyncGenerator[str, None]:
        url = self.STREAM_URL.format(model=self.model)
        payload = self._build_payload(messages)
        params = {"key": self.api_key, "alt": "sse"}

        client = await get_shared_client()
        async with client.stream("POST", url, params=params, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        chunk = json.loads(line[6:])
                        candidates = chunk.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text", "")
                                if text:
                                    yield text
                    except json.JSONDecodeError:
                        continue

    async def test_connection(self) -> tuple[bool, str]:
        """모델 목록 API로 경량 연결 테스트 (토큰 소비 없음)"""
        try:
            params = {"key": self.api_key}
            client = await get_shared_client()
            response = await client.get(self.MODELS_URL, params=params)
            response.raise_for_status()
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

    # OpenAI 모델 감지 (gpt-3.5, gpt-4, gpt-4o, o1, o3 등)
    if any(x in model_lower for x in ["gpt-", "o1", "o3", "chatgpt"]):
        return OpenAIProvider(api_key, model, temperature, max_tokens)
    elif "claude" in model_lower:
        return AnthropicProvider(api_key, model, temperature, max_tokens)
    elif "gemini" in model_lower:
        return GoogleProvider(api_key, model, temperature, max_tokens)

    # 기본값: OpenAI 호환 API
    return OpenAIProvider(api_key, model, temperature, max_tokens)
