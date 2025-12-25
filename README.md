# 📖 Lexicon

**Lexicon**은 언어 학습을 위한 인터랙티브 퀴즈 애플리케이션입니다. 커스터마이징 가능한 설정, AI 학습 도우미, 실시간 통계 추적 등의 기능을 제공합니다.

![Lexicon](static/icon.ico)

## ✨ 주요 기능

### 📝 다양한 퀴즈 유형
- **객관식**: 4지선다형 문제로 빠른 학습
- **주관식**: 직접 입력하여 정확한 암기 확인
- **이미지 퀴즈**: 시각적 학습 지원

### 🤖 AI 학습 도우미
- LLM 기반 실시간 질문 응답
- 맞춤형 페르소나 설정
- 채팅 기록 관리

### 📊 실시간 통계
- 정답률 추적
- 총 문제 수, 정답/오답 개수 표시
- 헤더에서 한눈에 확인

### 🔊 TTS (음성 읽기)
- **더블클릭 읽기**: 문제 텍스트를 더블클릭하여 음성으로 듣기
- **네온 효과**: 읽는 동안 시각적 피드백
- **세부 설정**: 속도, 음높이, 볼륨 조정 가능
- **다국어 지원**: 자동 언어 감지 및 적절한 음성 선택

### ⚙️ 커스터마이징
- **언어 선택**: 다양한 언어 조합 (한국어, 일본어, 영어, 중국어 등)
- **출제 패턴**: A→B, B→A, 이미지→텍스트 등
- **출제 순서**: 무작위, 정순, 역순
- **주제 필터링**: 원하는 카테고리만 선택
- **폰트 설정**: 12가지 폰트 선택, 크기 조정 (대주제/문제/답)

### 📁 유연한 데이터 관리
- JSON 파일 기반 퀴즈 데이터
- 여러 파일 간 쉬운 전환
- 오답 노트 자동 저장

### 🎨 현대적인 UI/UX
- 다크/라이트 모드 자동 감지
- 반응형 디자인 (모바일 지원)
- 부드러운 애니메이션
- 직관적인 피드백 시스템 (O/X 표시)

## 🚀 시작하기

### 필수 요구사항
- Python 3.8+
- Node.js (선택사항, 프론트엔드 개발 시)

### 설치

1. **저장소 클론**
```bash
git clone https://github.com/duckgeunpark/Lexicon.git
cd Lexicon
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

### 실행

#### 웹 서버 모드
```bash
python run_server.py
```
브라우저에서 `http://localhost:8000` 접속

#### 데스크톱 앱 모드
```bash
python run_server.py --desktop
```
PyWebView 창이 자동으로 열립니다.

### 빌드 (실행 파일 생성)
```bash
python build.py
```
`dist/` 폴더에 실행 파일이 생성됩니다.

## 📂 프로젝트 구조

```
Lexicon/
├── app/                    # FastAPI 애플리케이션
│   ├── main.py            # API 라우터
│   └── models.py          # 데이터 모델
├── data/                   # 퀴즈 데이터
│   ├── config.json        # 설정 파일
│   ├── quiz.json          # 기본 퀴즈 데이터
│   └── quiz_wrong.json    # 오답 노트
├── static/                 # 프론트엔드 파일
│   ├── index.html         # 메인 HTML
│   ├── app.js             # JavaScript 로직
│   ├── styles.css         # 스타일시트
│   └── icon.ico           # 앱 아이콘
├── run_server.py          # 서버 실행 스크립트
├── build.py               # PyInstaller 빌드 스크립트
├── requirements.txt       # Python 의존성
└── README.md              # 이 문서
```

## ⚙️ 설정 파일 구조

`data/config.json`은 모든 앱 설정을 저장합니다:

```json
{
  "quiz_file": "quiz",
  "language1": "ja",
  "language2": "ko",
  "question_pattern": "A>B",
  "order_mode": "random",
  "selected_categories": ["학교", "일상"],

  "tts": {
    "rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0,
    "minNeonDuration": 500
  },

  "fonts": {
    "fontFamily": "'Gothic A1', sans-serif",
    "categorySize": 22,
    "questionSize": 72,
    "answerSize": 23
  },

  "llm": {
    "model": "claude-3-sonnet",
    "api_key": "your-api-key"
  }
}
```

## 🎮 사용 방법

### 1. 퀴즈 데이터 준비
`data/quiz.json` 형식:
```json
{
  "카테고리명": [
    {
      "ko": "한국어 텍스트",
      "ja": "日本語テキスト",
      "en": "English text",
      "image": "/static/images/example.png"
    }
  ]
}
```

### 2. 설정 구성
- 우측 상단 ⚙️ 버튼 클릭
- **퀴즈 설정**: 언어, 출제 패턴, 문제 유형 선택
- **폰트 설정**: 폰트 종류 선택 (12가지), 대주제/문제/답 크기 조정
- **TTS 설정**: 읽기 속도, 음높이, 볼륨, 네온 효과 지속시간 조정
- **JSON 파일**: 여러 퀴즈 파일 간 전환 지원
- 저장 후 자동 새로고침

### 3. LLM 설정 (선택사항)
- 우측 하단 상태 버튼 클릭
- LLM 모델 및 API 키 입력
- 페르소나, Temperature, Max Tokens 설정
- 저장 및 연결 테스트

### 4. 퀴즈 풀기
- 문제가 자동으로 로드됩니다
- **객관식**: 보기 클릭
- **주관식**: 답 입력 후 → 버튼 클릭
- **음성 듣기**: 문제 텍스트를 더블클릭하여 TTS로 발음 확인
- **AI 도우미**: 💡 버튼으로 질문 가능 (LLM 설정 필요)

## 🛠️ 기술 스택

### 백엔드
- **FastAPI**: 현대적이고 빠른 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증
- **HTTPX**: 비동기 HTTP 클라이언트 (LLM API)

### 프론트엔드
- **Vanilla JavaScript**: 프레임워크 없이 순수 JS
- **Web Speech API**: 브라우저 내장 TTS 기능
- **Google Fonts**: 다양한 폰트 지원
- **CSS Variables**: 다이나믹 테마
- **Perplexity Design System**: 모던한 UI 디자인

### 데스크톱
- **PyWebView**: 크로스플랫폼 데스크톱 앱
- **PyInstaller**: 실행 파일 빌드

## 🔧 개발

### 코드 스타일
- Python: PEP 8
- JavaScript: ESLint 권장 설정
- CSS: BEM 명명 규칙

### 디버깅
개발자 도구(F12)에서 콘솔 로그 확인:
```javascript
console.log('🚀 Lexicon App 초기화 중...');
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 문의

프로젝트 링크: [https://github.com/duckgeunpark/Lexicon](https://github.com/duckgeunpark/Lexicon)

---

**Made with ❤️ by DuckgeunPark**
