# Lexicon

**언어 학습 퀴즈 데스크톱 애플리케이션**

JSON 기반 퀴즈 데이터로 어휘를 학습하고, AI 도우미와 대화하며 복습할 수 있는 크로스플랫폼 데스크톱 앱입니다.

![Lexicon](static/icon.ico)

## 시연

<video src="https://github.com/user-attachments/assets/f7f654a9-45f9-4bd5-84ec-61d0b9ce3f7d"
       controls muted playsinline loop>
  브라우저에서 재생이 안 되면 <a href="https://github.com/user-attachments/assets/f7f654a9-45f9-4bd5-84ec-61d0b9ce3f7d">여기</a>를 클릭하세요.
</video>

---

## 주요 기능

### 퀴즈 시스템
- **객관식 / 주관식** 자동 출제
- **출제 패턴**: A→B, B→A, 이미지→텍스트 등 조합
- **출제 순서**: 무작위, 정순, 역순
- **카테고리 필터링**: 원하는 주제만 선택하여 학습
- **오답 노트 자동 저장** 및 오답 복습 모드

### AI 학습 도우미 (LLM)
- OpenAI, Anthropic, Google 멀티 프로바이더 지원
- SSE 스트리밍 응답으로 실시간 타이핑 효과
- 5종 페르소나 프리셋 (친절한 튜터, 엄격한 교수, 원어민 친구 등)
- 현재 풀고 있는 문제 컨텍스트를 자동 전달

### 학습 관리
- 실시간 정답률 통계 (헤더 상시 표시)
- 학습 진도 저장/복원 (서버 측 persist)
- 세션 누적 통계 (페이지 이탈 시 자동 저장)

### TTS 음성 읽기
- Web Speech API 기반 다국어 TTS
- 속도, 음높이, 볼륨 세부 조정
- 사운드 웨이브 애니메이션 + 진행 표시바

### 커스터마이징
- **12종 한글/일본어 폰트** 선택, 대주제/문제/답 크기 개별 조정
- **다크/라이트 테마** 수동 전환 (시스템 설정 연동 + 수동 토글)
- **키보드 단축키**: TTS(S), LLM(L), 리로드(R), 설정(?) 등

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Backend** | FastAPI, Uvicorn, Pydantic v2 |
| **Frontend** | Vanilla JS, CSS Variables, Web Speech API |
| **Desktop** | PyWebView (네이티브 윈도우 래핑) |
| **LLM** | httpx AsyncClient, SSE Streaming |
| **빌드** | PyInstaller (단일 실행 파일) |

---

## 아키텍처

```
┌─────────────────────────────────────────────────┐
│  PyWebView (Desktop Window)                     │
│  ┌───────────────────────────────────────────┐  │
│  │  Frontend (Vanilla JS + CSS)              │  │
│  │  - Quiz UI, Settings Modal, LLM Chat      │  │
│  │  - TTS, Theme, Progress, Stats            │  │
│  └──────────────┬────────────────────────────┘  │
│                 │ HTTP (localhost:8000)         │
│  ┌──────────────▼────────────────────────────┐  │
│  │  FastAPI Server                           │  │
│  │  ├─ /api/quiz/*      퀴즈 엔진             │  │
│  │  ├─ /api/settings/*  설정 관리             │  │
│  │  └─ /api/llm/*       AI 채팅 + 스트리밍     │  │
│  │                                           │  │
│  │  Core Layer                               │  │
│  │  ├─ ConfigManager    (Thread-safe 싱글턴)  │  │
│  │  ├─ QuizDataLoader   (문제 풀 관리)        │  │
│  │  └─ LLMService       (멀티 프로바이더)     │  │
│  └──────────────┬────────────────────────────┘  │
│                 │                                │
│  ┌──────────────▼────────────────────────────┐  │
│  │  data/                                    │  │
│  │  ├─ config.json       설정 (모든 상태)     │  │
│  │  ├─ quiz.json         퀴즈 데이터          │  │
│  │  ├─ quiz_wrong.json   오답 노트            │  │
│  │  └─ img/              이미지 문제용         │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 프로젝트 구조

```
Lexicon/
├── app/
│   ├── api/endpoints/
│   │   ├── quiz.py          # 퀴즈 출제, 채점, 오답, 진도, 통계 API
│   │   ├── settings.py      # 설정 CRUD API (TTS, 폰트, 시스템)
│   │   └── llm.py           # LLM 설정, 채팅, 스트리밍 API
│   ├── core/
│   │   ├── config.py        # ConfigManager (Thread-safe 싱글턴)
│   │   ├── dependencies.py  # FastAPI DI (Depends)
│   │   └── exceptions.py    # 커스텀 HTTP 예외
│   ├── llm/
│   │   ├── providers.py     # OpenAI / Anthropic / Google 프로바이더
│   │   ├── service.py       # LLM 통합 서비스
│   │   └── prompts.py       # 페르소나 & 프롬프트 관리
│   ├── models/
│   │   ├── requests.py      # Pydantic 요청 모델
│   │   └── responses.py     # Pydantic 응답 모델
│   └── utils/
│       └── data_loader.py   # 퀴즈 데이터 로더 (Thread-safe)
├── static/
│   ├── index.html           # SPA 메인 페이지
│   ├── app.js               # 프론트엔드 로직 (2,100+ LOC)
│   └── styles.css           # 스타일 + 다크/라이트 테마 (2,900+ LOC)
├── data/
│   ├── config.json          # 앱 설정
│   ├── quiz.json            # 퀴즈 데이터
│   └── quiz_wrong.json      # 오답 노트
├── run_server.py            # FastAPI + PyWebView 엔트리포인트
├── build.py                 # PyInstaller 빌드 스크립트
└── requirements.txt
```

---

## 설계 포인트

### 보안
- **Path Traversal 방어**: 파일명 정규식 검증 (`_sanitize_filename`)
- **Pydantic 요청 검증**: 모든 POST 엔드포인트에 타입 모델 적용
- **API 키 마스킹**: 설정 조회 시 `sk-12...ab34` 형태로 마스킹
- **CORS 제한**: `localhost:8000`만 허용, GET/POST만 허용

### 동시성 & 안정성
- **Thread-safe ConfigManager**: `threading.Lock` 기반 싱글턴, 모든 읽기/쓰기 동기화
- **Thread-safe QuizDataLoader**: 문제 풀 재구성, 문제 생성에 Lock 적용
- **UUID 기반 문제 ID**: `random.randint` 대신 `uuid4().hex[:8]`으로 충돌 방지

### 성능
- **httpx AsyncClient 공유**: LLM API 호출 시 커넥션 풀 재사용
- **선택적 풀 재구성**: 카테고리/순서 변경 시에만 `rebuild_question_pool()` 호출
- **SSE 스트리밍**: LLM 응답을 청크 단위로 전송하여 체감 응답 속도 개선

### 확장성
- **멀티 프로바이더 LLM**: `LLMProvider` 추상 클래스 → OpenAI, Anthropic, Google 구현체
- **JSON 기반 퀴즈 데이터**: 파일만 추가하면 새 퀴즈셋 즉시 사용
- **ConfigManager 중앙화**: 모든 모듈이 단일 설정 소스 참조

---

## 시작하기

### 요구사항
- Python 3.8+

### 설치 및 실행

```bash
# 클론
git clone https://github.com/duckgeunpark/Lexicon.git
cd Lexicon

# 가상환경
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 실행
python run_server.py
```

### 실행 파일 빌드

```bash
python build.py
# → dist/ 폴더에 Lexicon.exe 생성
```

---

## 퀴즈 데이터 형식

`data/quiz.json`:

```json
{
  "카테고리명": {
    "문제": "답",
    "apple": "사과",
    "学校": "がっこう"
  }
}
```

- 카테고리를 자유롭게 추가/삭제
- `data/img/` 폴더에 이미지를 넣으면 이미지→텍스트 문제 자동 생성
- `quiz_*.json` 패턴으로 여러 퀴즈 파일을 만들고 설정에서 전환 가능

---

## 설정 구조

```json
{
  "quiz_file": "quiz",
  "language1": "ja",
  "language2": "en",
  "question_pattern": "A>B",
  "order_mode": "random",
  "selected_categories": ["hiragana", "katakana"],
  "tts": { "rate": 1.0, "pitch": 1.0, "volume": 1.0 },
  "fonts": { "fontFamily": "'Noto Sans KR'", "questionSize": 72 },
  "llm": { "model": "gpt-4o-mini", "api_key": "..." },
  "llm_prompts": { "persona": "friendly_tutor", "temperature": 0.7 },
  "system": { "nextQuestionDelay": 500, "shortcuts": { "tts": "S" } }
}
```

---

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/quiz/next` | 다음 문제 출제 |
| POST | `/api/quiz/check-answer` | 답안 채점 |
| POST | `/api/quiz/save-wrong-answer` | 오답 저장 |
| GET | `/api/quiz/wrong-answers` | 오답 목록 조회 |
| POST | `/api/quiz/review-wrong` | 오답 복습 문제 출제 |
| GET/POST | `/api/quiz/progress` | 학습 진도 조회/저장 |
| GET/POST | `/api/quiz/session-stats` | 세션 통계 조회/저장 |
| GET/POST | `/api/settings/` | 전체 설정 조회/저장 |
| GET/POST | `/api/settings/tts` | TTS 설정 |
| GET/POST | `/api/settings/fonts` | 폰트 설정 |
| POST | `/api/llm/chat` | LLM 채팅 |
| POST | `/api/llm/chat/stream` | LLM 스트리밍 (SSE) |
| POST | `/api/llm/test` | LLM 연결 테스트 |

---

## 라이선스

MIT License

---

**Made with by DuckgeunPark**
