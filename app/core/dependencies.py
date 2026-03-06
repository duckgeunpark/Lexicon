"""
FastAPI 의존성 주입
"""
from ..utils.data_loader import QuizDataLoader, quiz_loader
from .config import ConfigManager


def get_quiz_loader() -> QuizDataLoader:
    """QuizDataLoader 의존성"""
    return quiz_loader


def get_config_manager() -> ConfigManager:
    """ConfigManager 의존성"""
    return ConfigManager.get_instance()
