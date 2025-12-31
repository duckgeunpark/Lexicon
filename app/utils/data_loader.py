import json
import os
from pathlib import Path
from typing import Dict, List
import random


class QuizDataLoader:
    """퀴즈 데이터 로드 및 관리 클래스"""

    def __init__(self, data_dir: str = "data", images_dir: str = "images"):
        self.data_dir = Path(data_dir)
        self.images_dir = Path(images_dir)
        self.quiz_data = {}
        self.config = {}
        self.available_images = set()
        self.use_categories = False  # 카테고리 사용 여부
        self.current_filename = "quiz"  # 현재 파일명
        self.question_pool = []  # 문제 풀
        self.current_index = 0  # 현재 인덱스
        self.reload()

    def reload(self, filename: str = None):
        """데이터 및 설정 다시 로드"""
        self.load_config()

        # 파일명이 주어지지 않으면 config에서 읽기
        if filename is None:
            filename = self.config.get("quiz_file", "quiz")

        self.load_quiz_data(filename)
        self.scan_images()
        self.rebuild_question_pool()  # 문제 풀 재구성

    def get_available_json_files(self) -> List[str]:
        """data 디렉토리의 사용 가능한 JSON 파일 목록 반환"""
        json_files = []
        if self.data_dir.exists():
            for file in self.data_dir.glob("*.json"):
                # config.json은 제외
                if file.name != "config.json":
                    json_files.append(file.stem)  # 확장자 없는 파일명
        return sorted(json_files)

    def load_config(self):
        """config.json 로드"""
        config_path = self.data_dir / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 기본 설정
            self.config = {
                "language1": "ko",
                "language2": "en",
                "question_pattern": "random",
                "random_patterns": {
                    "A>B": True,
                    "B>A": True,
                    "img>A": True,
                    "img>B": True,
                    "img>A,B": True
                },
                "quiz_type": "random",
                "quiz_types": {
                    "multiple_choice": True,
                    "subjective": True
                },
                "order_mode": "random",
                "quiz_file": "quiz"  # 기본 파일명
            }

    def save_config(self):
        """config.json 저장"""
        config_path = self.data_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def load_quiz_data(self, filename: str = "quiz.json"):
        """quiz.json 로드 (카테고리 구조 지원)"""
        # 파일명에서 .json 확장자 제거 (있으면)
        base_filename = filename.replace('.json', '')
        self.current_filename = base_filename

        quiz_path = self.data_dir / f"{base_filename}.json"
        if quiz_path.exists():
            with open(quiz_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

                # 새로운 카테고리 구조 감지
                # 첫 번째 값이 dict면 카테고리 구조
                if raw_data and isinstance(next(iter(raw_data.values()), None), dict):
                    self.quiz_data = raw_data
                    self.use_categories = True
                else:
                    # 기존 flat 구조는 'default' 카테고리로 변환
                    self.quiz_data = {"default": raw_data}
                    self.use_categories = False
        else:
            # 기본 샘플 데이터
            self.quiz_data = {
                "default": {
                    "사과": "apple",
                    "바나나": "banana",
                    "포도": "grape"
                }
            }
            self.use_categories = False

    def scan_images(self):
        """images 폴더 스캔"""
        self.available_images = set()
        if self.images_dir.exists():
            for file in self.images_dir.glob("*.png"):
                self.available_images.add(file.stem)
            for file in self.images_dir.glob("*.jpg"):
                self.available_images.add(file.stem)
            for file in self.images_dir.glob("*.jpeg"):
                self.available_images.add(file.stem)

    def detect_language(self, text: str) -> str:
        """텍스트의 언어 감지"""
        if not text:
            return 'en'

        import re

        # 한글 감지
        if re.search(r'[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]', text):
            return 'ko'

        # 일본어 감지 (히라가나, 가타카나)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return 'ja'

        # 중국어 감지
        if re.search(r'[\u4E00-\u9FFF]', text):
            return 'zh'

        # 스페인어 특수문자 감지
        if re.search(r'[áéíóúñ¿¡]', text, re.IGNORECASE):
            return 'es'

        # 프랑스어 특수문자 감지
        if re.search(r'[àâäçèéêëîïôùûü]', text, re.IGNORECASE):
            return 'fr'

        # 기본값: 영어 (로마자)
        return 'en'

    def detect_quiz_languages(self) -> Dict:
        """퀴즈 데이터에서 언어 자동 감지"""
        if not self.quiz_data:
            return {'language1': 'en', 'language2': 'en'}

        # 첫 번째 카테고리의 첫 번째 항목에서 샘플링
        categories = list(self.quiz_data.keys())
        if not categories:
            return {'language1': 'en', 'language2': 'en'}

        first_category = categories[0]
        category_data = self.quiz_data[first_category]

        if not category_data:
            return {'language1': 'en', 'language2': 'en'}

        # 첫 번째 항목 가져오기
        sample_key = next(iter(category_data.keys()))
        sample_value = category_data[sample_key]

        return {
            'language1': self.detect_language(sample_key),
            'language2': self.detect_language(sample_value)
        }

    def get_random_pattern(self, has_image: bool = False) -> str:
        """랜덤 패턴 선택 (이미지 유무 고려)"""
        if self.config.get("question_pattern") == "random":
            enabled_patterns = []

            for pattern, enabled in self.config.get("random_patterns", {}).items():
                if not enabled:
                    continue

                # 이미지가 없으면 img> 패턴 제외
                if pattern.startswith("img>") and not has_image:
                    continue

                enabled_patterns.append(pattern)

            if enabled_patterns:
                return random.choice(enabled_patterns)

            # fallback: 이미지 없으면 A>B 또는 B>A만
            return random.choice(["A>B", "B>A"])

        # 고정 패턴이 설정된 경우
        pattern = self.config.get("question_pattern", "A>B")

        # 이미지가 없는데 img> 패턴이면 fallback
        if pattern.startswith("img>") and not has_image:
            return "A>B"

        return pattern

    def get_random_quiz_type(self) -> str:
        """랜덤 퀴즈 타입 선택"""
        if self.config.get("quiz_type") == "random":
            enabled_types = [
                qtype for qtype, enabled
                in self.config.get("quiz_types", {}).items()
                if enabled
            ]
            if enabled_types:
                return random.choice(enabled_types)
        return self.config.get("quiz_type", "multiple_choice")

    def rebuild_question_pool(self):
        """선택된 카테고리의 문제들로 문제 풀 재구성"""
        self.question_pool = []
        self.current_index = 0

        if not self.quiz_data:
            return

        # 선택된 카테고리 가져오기 (없으면 전체)
        selected_categories = self.config.get("selected_categories", list(self.quiz_data.keys()))

        # 선택된 카테고리가 비어있으면 전체 선택
        if not selected_categories:
            selected_categories = list(self.quiz_data.keys())

        # 선택된 카테고리의 모든 문제를 풀에 추가
        for category in selected_categories:
            if category in self.quiz_data:
                category_items = self.quiz_data[category]
                for lang1, lang2 in category_items.items():
                    self.question_pool.append({
                        "category": category,
                        "lang1": lang1,
                        "lang2": lang2
                    })

        # 출제 순서에 따라 정렬
        order_mode = self.config.get("order_mode", "random")

        if order_mode == "random":
            random.shuffle(self.question_pool)
        elif order_mode == "backward":
            self.question_pool.reverse()
        # forward는 그대로 유지

    def generate_quiz_question(self) -> Dict:
        """퀴즈 문제 생성 (카테고리 지원, 순서 및 중복 방지)"""
        if not self.quiz_data:
            return None

        # 문제 풀이 비어있거나 모두 소진된 경우 재구성
        if not self.question_pool or self.current_index >= len(self.question_pool):
            self.rebuild_question_pool()

        # 문제 풀이 여전히 비어있으면 None 반환
        if not self.question_pool:
            return None

        # 현재 인덱스의 문제 가져오기
        current_item = self.question_pool[self.current_index]
        selected_category = current_item["category"]
        correct_lang1 = current_item["lang1"]
        correct_lang2 = current_item["lang2"]

        # 인덱스 증가 (다음 문제로)
        self.current_index += 1

        # 이미지 확인
        has_image = correct_lang1 in self.available_images
        image_path = f"/images/{correct_lang1}.png" if has_image else None

        # 패턴 및 타입 선택 (이미지 유무 고려)
        pattern = self.get_random_pattern(has_image)
        quiz_type = self.get_random_quiz_type()

        # 문제 생성
        question = self._create_question(pattern, correct_lang1, correct_lang2, image_path)

        # 카테고리 정보 추가 (default가 아닌 경우에만)
        if selected_category != "default":
            question["category"] = selected_category
        else:
            question["category"] = None

        # 객관식인 경우 보기 생성
        if quiz_type == "multiple_choice":
            # 같은 카테고리의 다른 문제들을 오답 보기로 사용
            category_items = self.quiz_data[selected_category]
            lang1_items = list(category_items.keys())
            options = self._create_options(pattern, correct_lang1, correct_lang2, image_path, lang1_items, selected_category)
            question["options"] = options

        # 프론트엔드 호환을 위한 필드명 변경
        question["type"] = quiz_type  # quiz_type → type
        question["pattern"] = pattern

        # image → image_path로 필드명 통일
        if question.get("image"):
            question["image_path"] = question.pop("image")

        return question

    def _create_question(self, pattern: str, lang1: str, lang2: str, image_path: str) -> Dict:
        """패턴에 따른 문제 생성"""
        question_id = f"q_{random.randint(1000, 9999)}"

        if pattern == "A>B":
            return {
                "id": question_id,
                "question": lang1,
                "question_type": "text",
                "answer": lang2,
                "answer_type": "text",
                "image": None,
                "original_question": lang1,  # 원본 A (lang1)
                "original_answer": lang2     # 원본 B (lang2)
            }

        elif pattern == "B>A":
            return {
                "id": question_id,
                "question": lang2,
                "question_type": "text",
                "answer": lang1,
                "answer_type": "text",
                "image": None,
                "original_question": lang1,  # 원본 A (lang1)
                "original_answer": lang2     # 원본 B (lang2)
            }

        elif pattern == "img>A":
            # 이미지가 있어야만 이 패턴 사용
            if not image_path:
                return self._create_question("A>B", lang1, lang2, None)

            return {
                "id": question_id,
                "question": "이 이미지는 무엇일까요?",
                "question_type": "image",
                "answer": lang1,
                "answer_type": "text",
                "image": image_path,
                "original_question": lang1,  # 원본 A (lang1)
                "original_answer": lang2     # 원본 B (lang2)
            }

        elif pattern == "img>B":
            # 이미지가 있어야만 이 패턴 사용
            if not image_path:
                return self._create_question("A>B", lang1, lang2, None)

            return {
                "id": question_id,
                "question": "What is this?",
                "question_type": "image",
                "answer": lang2,
                "answer_type": "text",
                "image": image_path,
                "original_question": lang1,  # 원본 A (lang1)
                "original_answer": lang2     # 원본 B (lang2)
            }

        elif pattern == "img>A,B":
            # 이미지가 있어야만 이 패턴 사용
            if not image_path:
                return self._create_question("A>B", lang1, lang2, None)

            return {
                "id": question_id,
                "question": "이 이미지는?",
                "question_type": "image",
                "answer": f"{lang1} / {lang2}",
                "answer_type": "text",
                "image": image_path,
                "original_question": lang1,  # 원본 A (lang1)
                "original_answer": lang2     # 원본 B (lang2)
            }

        # 기본값
        return {
            "id": question_id,
            "question": lang1,
            "question_type": "text",
            "answer": lang2,
            "answer_type": "text",
            "image": None,
            "original_question": lang1,  # 원본 A (lang1)
            "original_answer": lang2     # 원본 B (lang2)
        }

    def _create_options(self, pattern: str, correct_lang1: str, correct_lang2: str,
                       image_path: str, all_items: List[str], category: str) -> List[Dict]:
        """객관식 보기 생성 (4지선다)"""
        options = []

        # 오답 3개 선택 (정답과 다른 것만)
        wrong_items = [item for item in all_items if item != correct_lang1]

        if len(wrong_items) >= 3:
            wrong_choices = random.sample(wrong_items, 3)
        else:
            # 데이터가 4개 미만인 경우 중복 허용
            wrong_choices = random.choices(wrong_items, k=3) if wrong_items else []

        # 카테고리의 데이터 가져오기
        category_data = self.quiz_data[category]

        # 패턴에 따라 정답 및 오답 텍스트 결정
        if pattern in ["A>B", "img>B"]:
            # 정답이 lang2 (영어)
            correct_text = correct_lang2
            wrong_texts = [category_data[item] for item in wrong_choices]

        elif pattern in ["B>A", "img>A"]:
            # 정답이 lang1 (한국어)
            correct_text = correct_lang1
            wrong_texts = wrong_choices

        elif pattern == "img>A,B":
            # 정답이 "한국어 / 영어" 형식
            correct_text = f"{correct_lang1} / {correct_lang2}"
            wrong_texts = [f"{item} / {category_data[item]}" for item in wrong_choices]

        else:
            # 기본값 (A>B)
            correct_text = correct_lang2
            wrong_texts = [category_data[item] for item in wrong_choices]

        # 전체 선택지 생성 (정답 + 오답)
        all_choices = [correct_text] + wrong_texts

        # 섞기
        random.shuffle(all_choices)

        # 옵션 객체 생성
        for idx, choice in enumerate(all_choices):
            options.append({
                "id": f"opt_{idx}",
                "text": choice,
                "is_correct": choice == correct_text
            })

        return options


# 전역 인스턴스
quiz_loader = QuizDataLoader()
