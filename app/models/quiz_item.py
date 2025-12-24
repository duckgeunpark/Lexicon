from pydantic import BaseModel
from typing import List, Optional


class QuizOption(BaseModel):
    """퀴즈 선택지 모델"""
    id: str
    text: str
    image: Optional[str] = None
    language: str  # 'ko', 'en', 'ja' 등


class QuizQuestion(BaseModel):
    """퀴즈 문제 모델"""
    id: str
    type: str  # 'text-to-text', 'text-to-image', 'image-to-text'
    question: str
    options: List[QuizOption]
    correct_answer: str
    difficulty: str  # 'easy', 'medium', 'hard'


class QuizResult(BaseModel):
    """퀴즈 결과 모델"""
    question_id: str
    user_answer: str
    is_correct: bool
    time_spent: float  # seconds


class QuizSession(BaseModel):
    """퀴즈 세션 모델"""
    session_id: str
    total_questions: int
    correct_answers: int
    results: List[QuizResult]
