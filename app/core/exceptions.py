"""
앱 공통 예외 클래스
"""
from fastapi import HTTPException


class QuizNotFoundError(HTTPException):
    def __init__(self, detail: str = "No quiz data available"):
        super().__init__(status_code=404, detail=detail)


class InvalidFileError(HTTPException):
    def __init__(self, detail: str = "Invalid file"):
        super().__init__(status_code=400, detail=detail)


class ConfigError(HTTPException):
    def __init__(self, detail: str = "Configuration error"):
        super().__init__(status_code=500, detail=detail)


class LLMConfigError(HTTPException):
    def __init__(self, detail: str = "LLM configuration missing"):
        super().__init__(status_code=400, detail=detail)
