// Lexicon Quiz App - Frontend JavaScript

// ============ 전역 변수 ============
const API_BASE = '/api';
let currentQuestion = null;
let stats = {
    total: 0,
    correct: 0,
    incorrect: 0
};
let originalQuizFile = null;  // 설정 열 때의 원래 파일 저장
let originalFontSettings = null;  // 설정 열 때의 원래 폰트 설정 저장
let isReviewMode = false;  // 오답 복습 모드
let sessionStartTime = Date.now();  // 세션 시작 시간

// 시스템 설정
let systemSettings = {
    nextQuestionDelay: 1500,
    shortcuts: {
        tts: 'S',
        llm: 'L',
        reload: 'R',
        settings: ',',
        exit: 'Escape'
    }
};

// ============ DOM 요소 ============
const elements = {
    loading: document.getElementById('loading'),
    quizCard: document.getElementById('quizCard'),
    questionText: document.getElementById('questionText'),
    questionImage: document.getElementById('questionImage'),
    categoryLabel: document.getElementById('categoryLabel'),
    answerFeedback: document.getElementById('answerFeedback'),
    correctAnswerDisplay: document.getElementById('correctAnswerDisplay'),
    customAlert: document.getElementById('customAlert'),
    optionsGrid: document.getElementById('optionsGrid'),
    subjectiveContainer: document.getElementById('subjectiveContainer'),
    subjectiveInput: document.getElementById('subjectiveInput'),
    submitBtn: document.getElementById('submitBtn'),
    settingsBtn: document.getElementById('settingsBtn'),
    reloadBtn: document.getElementById('reloadBtn'),
    settingsModal: document.getElementById('settingsModal'),
    closeModal: document.getElementById('closeModal'),
    cancelBtn: document.getElementById('cancelBtn'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),
    ttsRate: document.getElementById('ttsRate'),
    ttsPitch: document.getElementById('ttsPitch'),
    ttsVolume: document.getElementById('ttsVolume'),
    ttsNeon: document.getElementById('ttsNeon'),
    ttsRateValue: document.getElementById('ttsRateValue'),
    ttsPitchValue: document.getElementById('ttsPitchValue'),
    ttsVolumeValue: document.getElementById('ttsVolumeValue'),
    ttsNeonValue: document.getElementById('ttsNeonValue'),
    fontFamily: document.getElementById('fontFamily'),
    fontCategory: document.getElementById('fontCategory'),
    fontQuestion: document.getElementById('fontQuestion'),
    fontAnswer: document.getElementById('fontAnswer'),
    fontCategoryValue: document.getElementById('fontCategoryValue'),
    fontQuestionValue: document.getElementById('fontQuestionValue'),
    fontAnswerValue: document.getElementById('fontAnswerValue'),
    llmStatusBtn: document.getElementById('llmStatusBtn'),
    llmConfigModal: document.getElementById('llmConfigModal'),
    closeLlmConfigModal: document.getElementById('closeLlmConfigModal'),
    cancelLlmConfig: document.getElementById('cancelLlmConfig'),
    saveLlmConfig: document.getElementById('saveLlmConfig'),
    llmModel: document.getElementById('llmModel'),
    llmModelCustom: document.getElementById('llmModelCustom'),
    llmApiKey: document.getElementById('llmApiKey'),
    llmPersona: document.getElementById('llmPersona'),
    llmCustomPrompt: document.getElementById('llmCustomPrompt'),
    llmTemperature: document.getElementById('llmTemperature'),
    llmMaxTokens: document.getElementById('llmMaxTokens'),
    temperatureValue: document.getElementById('temperatureValue'),
    maxTokensValue: document.getElementById('maxTokensValue'),
    personaDescription: document.getElementById('personaDescription'),
    llmConnectionStatus: document.getElementById('llmConnectionStatus'),
    llmHelpBtn: document.getElementById('llmHelpBtn'),
    llmModal: document.getElementById('llmModal'),
    closeLlmModal: document.getElementById('closeLlmModal'),
    llmClearBtn: document.getElementById('llmClearBtn'),
    llmQuestionInput: document.getElementById('llmQuestionInput'),
    llmSendBtn: document.getElementById('llmSendBtn'),
    llmChatMessages: document.getElementById('llmChatMessages'),
    // 시스템 설정 관련
    nextQuestionDelay: document.getElementById('nextQuestionDelay'),
    nextQuestionDelayValue: document.getElementById('nextQuestionDelayValue'),
    shortcutTTS: document.getElementById('shortcutTTS'),
    shortcutLLM: document.getElementById('shortcutLLM'),
    shortcutReload: document.getElementById('shortcutReload'),
    shortcutSettings: document.getElementById('shortcutSettings'),
    shortcutExit: document.getElementById('shortcutExit'),
    // TTS 재생 중 표시
    ttsPlayingIndicator: document.getElementById('ttsPlayingIndicator'),
    ttsProgressBar: document.getElementById('ttsProgressBar'),
    speakerBtn: document.getElementById('speakerBtn'),
    // Phase 6: 새 버튼
    reviewWrongBtn: document.getElementById('reviewWrongBtn'),
    themeToggleBtn: document.getElementById('themeToggleBtn')
};

// ============ 초기화 ============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Lexicon App 초기화 중...');

    // 통계 초기화 (페이지 로드 시)
    resetStats();

    // 이벤트 리스너 등록
    initEventListeners();

    // 첫 문제 로드
    loadNextQuestion();

    // 설정 로드 (UI 업데이트용, TTS 설정 포함)
    loadSettings();

    // LLM 상태 확인
    checkLlmStatus();

    // loadAvailableFiles()는 설정 열 때 호출 (openSettings)

    // 설정 저장 후 새로고침 시 알림 표시
    if (sessionStorage.getItem('settings_saved') === 'true') {
        showToast('✅ 설정이 저장되고 새로고침되었습니다');
        sessionStorage.removeItem('settings_saved');
    }

    // Phase 6: 테마 복원
    restoreTheme();

    // Phase 6: 진도 복원
    loadProgress();

    // Phase 6: 세션 종료 시 통계 저장
    window.addEventListener('beforeunload', saveSessionOnExit);
});

// ============ 이벤트 리스너 ============
function initEventListeners() {
    elements.settingsBtn.addEventListener('click', openSettings);
    elements.closeModal.addEventListener('click', closeSettings);
    elements.cancelBtn.addEventListener('click', closeSettings);
    elements.saveSettingsBtn.addEventListener('click', saveSettings);
    elements.reloadBtn.addEventListener('click', reloadData);
    elements.submitBtn.addEventListener('click', submitSubjectiveAnswer);

    // 전역 키보드 이벤트 (객관식/주관식)
    document.addEventListener('keydown', handleGlobalKeyPress);

    // 스피커 아이콘 클릭 시 TTS 읽기
    const speakerBtn = document.getElementById('speakerBtn');
    if (speakerBtn) {
        speakerBtn.addEventListener('click', speakQuestion);
    }

    // 설정 섹션 접기/펼치기
    document.querySelectorAll('.collapsible-header').forEach(header => {
        header.addEventListener('click', toggleSection);
    });

    // 카테고리 전체 선택/해제
    document.getElementById('selectAllCategories')?.addEventListener('click', () => selectAllCategories(true));
    document.getElementById('deselectAllCategories')?.addEventListener('click', () => selectAllCategories(false));

    // LLM 설정 관련 이벤트 리스너
    elements.llmStatusBtn.addEventListener('click', openLlmConfig);
    elements.closeLlmConfigModal.addEventListener('click', closeLlmConfig);
    elements.cancelLlmConfig.addEventListener('click', closeLlmConfig);
    elements.saveLlmConfig.addEventListener('click', saveLlmConfiguration);
    elements.llmModel.addEventListener('change', toggleCustomModelInput);
    elements.llmPersona.addEventListener('change', updatePersonaDescription);
    elements.llmTemperature.addEventListener('input', updateTemperatureValue);
    elements.llmMaxTokens.addEventListener('input', updateMaxTokensValue);

    // LLM 질문 관련 이벤트 리스너
    elements.llmHelpBtn.addEventListener('click', openLlmHelp);
    elements.closeLlmModal.addEventListener('click', closeLlmHelp);
    elements.llmClearBtn.addEventListener('click', clearLlmChat);
    elements.llmSendBtn.addEventListener('click', sendLlmQuestion);

    // Enter 키로 LLM 질문 전송 (Shift+Enter는 줄바꿈)
    elements.llmQuestionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendLlmQuestion();
        }
    });

    // 텍스트 입력 시 textarea 자동 높이 조절
    elements.llmQuestionInput.addEventListener('input', () => {
        elements.llmQuestionInput.style.height = 'auto';
        elements.llmQuestionInput.style.height = elements.llmQuestionInput.scrollHeight + 'px';
    });

    // TTS 설정 슬라이더 이벤트 리스너
    elements.ttsRate.addEventListener('input', updateTtsRateValue);
    elements.ttsPitch.addEventListener('input', updateTtsPitchValue);
    elements.ttsVolume.addEventListener('input', updateTtsVolumeValue);
    elements.ttsNeon.addEventListener('input', updateTtsNeonValue);

    // 폰트 설정 슬라이더 이벤트 리스너
    elements.fontFamily.addEventListener('change', applyFontSizes);
    elements.fontCategory.addEventListener('input', updateFontCategoryValue);
    elements.fontQuestion.addEventListener('input', updateFontQuestionValue);
    elements.fontAnswer.addEventListener('input', updateFontAnswerValue);

    // 시스템 설정 이벤트 리스너
    elements.nextQuestionDelay.addEventListener('input', updateNextQuestionDelayValue);

    // Phase 6: 테마 토글
    if (elements.themeToggleBtn) {
        elements.themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Phase 6: 오답 복습
    if (elements.reviewWrongBtn) {
        elements.reviewWrongBtn.addEventListener('click', toggleReviewMode);
    }
}

// ============ API 호출 ============
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API 오류 [${endpoint}]:`, error);
        throw error;
    }
}

// ============ 퀴즈 로드 ============
async function loadNextQuestion() {
    try {
        showLoading(true);
        const response = await apiCall('/quiz/next');

        if (response.success && response.data) {
            currentQuestion = response.data;
            displayQuestion(response.data);
        } else {
            showError('문제를 불러올 수 없습니다.');
        }
    } catch (error) {
        showError(`문제 로드 실패: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// ============ 문제 표시 ============
function displayQuestion(question) {
    // 카테고리 표시
    if (question.category) {
        elements.categoryLabel.textContent = question.category;
        elements.categoryLabel.style.display = 'block';
    } else {
        elements.categoryLabel.style.display = 'none';
    }

    // 이미지 표시
    if (question.image_path) {
        elements.questionImage.src = question.image_path;
        elements.questionImage.style.display = 'block';
        elements.questionText.textContent = '';
    } else {
        elements.questionImage.style.display = 'none';
        elements.questionText.textContent = question.question;
    }

    // 문제 유형에 따라 UI 변경
    if (question.type === 'multiple_choice') {
        displayMultipleChoice(question.options);
    } else {
        displaySubjective();
    }
}

function displayMultipleChoice(options) {
    elements.optionsGrid.style.display = 'grid';
    elements.subjectiveContainer.style.display = 'none';
    elements.optionsGrid.innerHTML = '';

    // 답 폰트 크기 가져오기
    const answerSize = elements.fontAnswer ? parseInt(elements.fontAnswer.value) : 20;

    options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-button';
        btn.setAttribute('data-index', index);

        // 번호 표시 추가
        const numberSpan = document.createElement('span');
        numberSpan.className = 'option-number';
        numberSpan.textContent = index + 1;

        // 텍스트 추가
        const textSpan = document.createElement('span');
        textSpan.textContent = option.text;
        textSpan.style.fontSize = `${answerSize}px`;

        btn.appendChild(numberSpan);
        btn.appendChild(textSpan);
        btn.onclick = () => selectAnswer(option, index);
        elements.optionsGrid.appendChild(btn);
    });
}

function displaySubjective() {
    elements.optionsGrid.style.display = 'none';
    elements.subjectiveContainer.style.display = 'flex';
    elements.subjectiveInput.value = '';
    elements.subjectiveInput.focus();
}

// ============ 전역 키보드 이벤트 핸들러 ============
function handleGlobalKeyPress(e) {
    // 입력 필드에 포커스가 있는 경우 (설정 모달의 단축키 입력 등)
    const isInputFocused = document.activeElement.tagName === 'INPUT' &&
                          document.activeElement !== elements.subjectiveInput;
    const isTextareaFocused = document.activeElement.tagName === 'TEXTAREA';

    // 모달 열림 상태 확인
    const isSettingsModalOpen = elements.settingsModal.style.display === 'flex';
    const isLlmModalOpen = elements.llmModal.style.display === 'flex';
    const isLlmConfigModalOpen = elements.llmConfigModal.style.display === 'flex';
    const isAnyModalOpen = isSettingsModalOpen || isLlmModalOpen || isLlmConfigModalOpen;

    // ESC 키 처리 (모달 닫기 또는 프로그램 종료)
    if (e.key === systemSettings.shortcuts.exit) {
        e.preventDefault();

        // 모달이 열려있으면 모달 닫기
        if (isSettingsModalOpen) {
            closeSettings();
            return;
        }
        if (isLlmModalOpen) {
            closeLlmHelp();
            return;
        }
        if (isLlmConfigModalOpen) {
            closeLlmConfig();
            return;
        }

        // 모달이 없으면 프로그램 종료
        if (confirm('정말 나가시겠습니까?')) {
            // 서버 종료 API 호출
            fetch('/api/shutdown', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(() => {
                // 응답 대기 없이 창 닫기 시도
                setTimeout(() => {
                    window.close();
                }, 200);
            }).catch(() => {
                // 실패해도 창 닫기 시도
                window.close();
            });
        }
        return;
    }

    // 단축키 처리 (모달이 열려있지 않고, 입력 필드에 포커스가 없을 때)
    if (!isAnyModalOpen && !isInputFocused && !isTextareaFocused) {
        const key = e.key.toUpperCase();

        // TTS 듣기
        if (key === systemSettings.shortcuts.tts.toUpperCase()) {
            e.preventDefault();
            speakQuestion();
            return;
        }

        // LLM 도우미
        if (key === systemSettings.shortcuts.llm.toUpperCase()) {
            e.preventDefault();
            openLlmHelp();
            return;
        }

        // 새로고침
        if (key === systemSettings.shortcuts.reload.toUpperCase()) {
            e.preventDefault();
            reloadData();
            return;
        }

        // 설정
        if (key === systemSettings.shortcuts.settings.toUpperCase()) {
            e.preventDefault();
            openSettings();
            return;
        }
    }

    // 모달이 열려있으면 이하 처리 무시
    if (isAnyModalOpen) return;

    // 주관식 처리
    if (elements.subjectiveContainer.style.display === 'flex') {
        if (e.key === 'Enter') {
            e.preventDefault();

            // 입력 필드에 포커스가 없으면 포커스
            if (document.activeElement !== elements.subjectiveInput) {
                elements.subjectiveInput.focus();
            } else {
                // 포커스가 있으면 제출
                submitSubjectiveAnswer();
            }
        }
        return;
    }

    // 객관식 처리 (1, 2, 3, 4 키)
    if (elements.optionsGrid.style.display === 'grid') {
        const key = e.key;
        if (['1', '2', '3', '4'].includes(key)) {
            e.preventDefault();
            const index = parseInt(key) - 1;
            const buttons = elements.optionsGrid.querySelectorAll('.option-button');

            if (buttons[index] && !buttons[index].disabled) {
                buttons[index].click();
            }
        }
    }
}

// ============ 답안 피드백 표시 ============
function showAnswerFeedback(isCorrect) {
    let feedback = elements.answerFeedback;

    // 요소가 없으면 동적으로 생성
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.id = 'answerFeedback';
        feedback.className = 'answer-feedback';
        document.body.appendChild(feedback);
        elements.answerFeedback = feedback;
    }

    feedback.textContent = isCorrect ? '○' : '✕';
    feedback.className = 'answer-feedback show ' + (isCorrect ? 'correct' : 'incorrect');

    // 1.2초 후 페이드아웃
    setTimeout(() => {
        feedback.classList.remove('show');
    }, 1200);
}

// ============ 커스텀 알림 ============
function showCustomAlert(message, duration = 2000) {
    elements.customAlert.textContent = message;
    elements.customAlert.style.display = 'block';

    setTimeout(() => {
        elements.customAlert.style.display = 'none';
    }, duration);
}

// ============ 답안 처리 ============
async function selectAnswer(option, index) {
    const buttons = elements.optionsGrid.querySelectorAll('.option-button');
    buttons.forEach(btn => btn.disabled = true);

    // 서버에서 is_correct를 보내지 않으므로, answer 필드로 정답 여부 판별
    const isCorrect = option.text === currentQuestion.answer;

    // 정답 표시
    buttons[index].classList.add(isCorrect ? 'correct' : 'incorrect');

    // O/X 피드백 표시
    showAnswerFeedback(isCorrect);

    if (!isCorrect) {
        // 오답인 경우 정답 표시
        buttons.forEach((btn, i) => {
            if (currentQuestion.options[i].text === currentQuestion.answer) {
                btn.classList.add('correct');
            }
        });

        // 오답 저장
        await saveWrongAnswer();
    }

    // 통계 업데이트
    updateStats(isCorrect);

    // 다음 문제로 (시스템 설정의 딜레이 적용)
    setTimeout(loadNextQuestion, systemSettings.nextQuestionDelay);
}

async function submitSubjectiveAnswer() {
    const userAnswer = elements.subjectiveInput.value.trim();

    if (!userAnswer) {
        // alert 대신 correctAnswerDisplay에 표시
        elements.correctAnswerDisplay.innerHTML = `
            <strong>답을 입력해주세요</strong>
        `;
        elements.correctAnswerDisplay.style.display = 'block';

        // 1.5초 후 자동으로 사라짐
        setTimeout(() => {
            elements.correctAnswerDisplay.style.display = 'none';
        }, 1500);

        return;
    }

    try {
        elements.submitBtn.disabled = true;
        elements.subjectiveInput.disabled = true;

        const response = await apiCall('/quiz/check-answer', {
            method: 'POST',
            body: JSON.stringify({
                user_answer: userAnswer,
                correct_answer: currentQuestion.answer,
                question: currentQuestion.question,
                category: currentQuestion.category
            })
        });

        if (response.success) {
            const isCorrect = response.is_correct;

            // 결과 표시
            elements.subjectiveInput.classList.add(isCorrect ? 'correct' : 'incorrect');

            // O/X 피드백 표시
            showAnswerFeedback(isCorrect);

            if (!isCorrect) {
                // 정답 표시 (alert 대신)
                elements.correctAnswerDisplay.innerHTML = `
                    <strong>오답입니다!</strong>
                    <div class="answer-text">정답: ${response.correct_answer}</div>
                `;
                elements.correctAnswerDisplay.style.display = 'block';
                await saveWrongAnswer();
            }

            updateStats(isCorrect);
            setTimeout(() => {
                elements.subjectiveInput.classList.remove('correct', 'incorrect');
                elements.correctAnswerDisplay.style.display = 'none';
                loadNextQuestion();
            }, systemSettings.nextQuestionDelay);
        }
    } catch (error) {
        showCustomAlert(`답안 확인 실패: ${error.message}`);
    } finally {
        elements.submitBtn.disabled = false;
        elements.subjectiveInput.disabled = false;
    }
}

// ============ 통계 관리 ============
function resetStats() {
    stats.total = 0;
    stats.correct = 0;
    stats.incorrect = 0;

    document.getElementById('headerStatTotal').textContent = '0';
    document.getElementById('headerStatCorrect').textContent = '0';
    document.getElementById('headerStatIncorrect').textContent = '0';
    document.getElementById('headerStatAccuracy').textContent = '0%';
}

function updateStats(isCorrect) {
    stats.total++;
    if (isCorrect) {
        stats.correct++;
    } else {
        stats.incorrect++;
    }

    updateStatsDisplay();

    // Phase 6: 자동 진도 저장 (10문제마다)
    if (stats.total % 10 === 0) {
        saveProgress();
    }
}

// ============ 오답 저장 ============
async function saveWrongAnswer() {
    try {
        // 원본 형식(A>B)으로 저장
        const originalQuestion = currentQuestion.original_question || currentQuestion.question;
        const originalAnswer = currentQuestion.original_answer || currentQuestion.answer;

        await apiCall('/quiz/save-wrong-answer', {
            method: 'POST',
            body: JSON.stringify({
                category: currentQuestion.category,
                question: originalQuestion,
                answer: originalAnswer
            })
        });
    } catch (error) {
        console.error('오답 저장 실패:', error);
    }
}

// ============ 언어 감지 ============
function detectLanguage(text) {
    if (!text) return 'en';

    // 한글 감지
    if (/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/.test(text)) {
        return 'ko';
    }

    // 일본어 감지 (히라가나, 가타카나)
    if (/[\u3040-\u309F\u30A0-\u30FF]/.test(text)) {
        return 'ja';
    }

    // 중국어 감지
    if (/[\u4E00-\u9FFF]/.test(text)) {
        return 'zh';
    }

    // 스페인어 특수문자 감지
    if (/[áéíóúñ¿¡]/i.test(text)) {
        return 'es';
    }

    // 프랑스어 특수문자 감지
    if (/[àâäçèéêëîïôùûü]/i.test(text)) {
        return 'fr';
    }

    // 기본값: 영어 (로마자)
    return 'en';
}

function detectLanguagesFromQuizData(quizData) {
    // 첫 번째 카테고리의 첫 번째 항목에서 샘플링
    const categories = Object.keys(quizData);
    if (categories.length === 0) {
        return { language1: 'en', language2: 'en' };
    }

    const firstCategory = categories[0];
    const categoryData = quizData[firstCategory];
    const keys = Object.keys(categoryData);

    if (keys.length === 0) {
        return { language1: 'en', language2: 'en' };
    }

    const sampleKey = keys[0];
    const sampleValue = categoryData[sampleKey];

    return {
        language1: detectLanguage(sampleKey),
        language2: detectLanguage(sampleValue)
    };
}

// ============ TTS (Text-to-Speech) ============
let currentSpeech = null;  // 현재 재생 중인 speech 객체
let ttsProgressInterval = null;  // 프로그레스 바 업데이트 인터벌

// TTS 설정 (여기서 쉽게 조정 가능)
const TTS_CONFIG = {
    rate: 0.5,      // 읽기 속도 (0.1 ~ 10, 기본 1.0) - 높을수록 빠름
    pitch: 0.7,     // 음높이 (0 ~ 2, 기본 1.0) - 높을수록 고음
    volume: 2.0     // 볼륨 (0 ~ 1, 기본 1.0)
};

function speakQuestion() {
    // 브라우저가 Web Speech API를 지원하는지 확인
    if (!('speechSynthesis' in window)) {
        showCustomAlert('이 브라우저는 음성 읽기를 지원하지 않습니다.');
        return;
    }

    // 현재 문제가 없으면 종료
    if (!currentQuestion || !currentQuestion.question) {
        console.log('TTS: 문제가 없습니다');
        return;
    }

    // 이미 읽는 중이면 중지
    if (currentSpeech || window.speechSynthesis.speaking) {
        console.log('TTS: 중지');
        window.speechSynthesis.cancel();

        // 프로그레스 바 인터벌 정리
        if (ttsProgressInterval) {
            clearInterval(ttsProgressInterval);
            ttsProgressInterval = null;
        }

        // UI 정리
        hideTTSIndicator();
        currentSpeech = null;
        return;
    }

    const text = currentQuestion.question;
    const lang = detectLanguage(text);

    console.log('TTS 시작:', text, '언어:', lang);

    // 음성 목록 로드 대기
    const speak = () => {
        // 혹시 모를 이전 음성 정리
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }

        // 짧은 지연 후 음성 재생 (interrupted 에러 방지)
        setTimeout(() => {
            // SpeechSynthesisUtterance 객체 생성
            const utterance = new SpeechSynthesisUtterance(text);

            // 언어 코드를 BCP 47 형식으로 변환
            const langMap = {
                'ko': 'ko-KR',
                'ja': 'ja-JP',
                'zh': 'zh-CN',
                'es': 'es-ES',
                'fr': 'fr-FR',
                'en': 'en-US'
            };

            const targetLang = langMap[lang] || 'en-US';
            utterance.lang = targetLang;

            // 해당 언어의 음성 선택 (사용 가능한 경우)
            const voices = window.speechSynthesis.getVoices();

            // 사용 가능한 모든 음성 로그 출력
            console.log('=== 사용 가능한 TTS 음성 목록 ===');
            voices.forEach((v, i) => {
                console.log(`${i + 1}. ${v.name} (${v.lang}) - ${v.localService ? 'Local' : 'Remote'}`);
            });
            console.log('============================');

            const voice = voices.find(v => v.lang.startsWith(lang)) || voices.find(v => v.lang.startsWith(targetLang));

            if (voice) {
                utterance.voice = voice;
                console.log('✓ 선택된 음성:', voice.name, voice.lang);
            } else {
                console.log('⚠️ ' + targetLang + ' 음성을 찾을 수 없음');

                // 영어가 아닌 경우에만 알림 표시하고 재생 중단
                if (lang !== 'en') {
                    const languageNames = {
                        'ko-KR': '한국어',
                        'ja-JP': '일본어',
                        'zh-CN': '중국어',
                        'es-ES': '스페인어',
                        'fr-FR': '프랑스어'
                    };
                    const langName = languageNames[targetLang] || targetLang;

                    showCustomAlert(`${langName} 음성이 없습니다. \n Windows 설정에서 음성을 설치하세요.`);

                    // TTS 재생 중단
                    return;
                }

                // 영어인 경우는 기본 음성으로 계속 재생
                console.log('→ 영어: 기본 음성으로 재생');
            }

            utterance.rate = TTS_CONFIG.rate;      // 읽기 속도
            utterance.pitch = TTS_CONFIG.pitch;    // 음높이
            utterance.volume = TTS_CONFIG.volume;  // 볼륨

            let speechStartTime = null;  // 음성 시작 시간 기록
            let estimatedDuration = null;  // 예상 재생 시간

            // 읽기 시작 시 음파 애니메이션 표시
            utterance.onstart = () => {
                console.log('TTS: 시작됨');
                speechStartTime = Date.now();
                currentSpeech = utterance;

                // 예상 재생 시간 계산 (글자 수 기반, rate 고려)
                // 평균적으로 영어는 분당 150단어, 한국어/일본어는 분당 300자 정도
                const wordsPerMinute = lang === 'en' ? 150 : 300;
                const charactersPerMinute = wordsPerMinute * (lang === 'en' ? 5 : 1);
                const baseMs = (text.length / charactersPerMinute) * 60 * 1000;
                estimatedDuration = baseMs / TTS_CONFIG.rate;

                // TTS 재생 중 표시
                showTTSIndicator(estimatedDuration);
            };

            // 읽기 종료 시 표시 제거
            utterance.onend = () => {
                console.log('TTS: 종료됨');
                hideTTSIndicator();
                currentSpeech = null;
            };

            // 에러 발생 시 표시 제거
            utterance.onerror = (event) => {
                console.error('TTS 에러:', event.error);

                // interrupted와 canceled 에러는 무시 (정상적인 중단)
                if (event.error !== 'canceled' && event.error !== 'interrupted') {
                    showCustomAlert(`음성 읽기 오류: ${event.error}`);
                }

                hideTTSIndicator();
                currentSpeech = null;
            };

            // 음성 재생 시작
            window.speechSynthesis.speak(utterance);
            console.log('TTS: speak() 호출됨');
        }, 100); // 100ms 지연
    };

    // 음성 목록이 로드될 때까지 대기
    const voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) {
        console.log('음성 로딩 중...');
        // 일회성 이벤트 리스너 사용
        const handleVoicesChanged = () => {
            console.log('음성 로드 완료');
            window.speechSynthesis.removeEventListener('voiceschanged', handleVoicesChanged);
            speak();
        };
        window.speechSynthesis.addEventListener('voiceschanged', handleVoicesChanged);
    } else {
        console.log('음성 이미 로드됨:', voices.length, '개');
        speak();
    }
}

// TTS 재생 중 표시 함수
function showTTSIndicator(estimatedDuration) {
    // 표시 요소 보이기
    elements.ttsPlayingIndicator.style.display = 'flex';
    elements.speakerBtn.classList.add('playing');

    // 프로그레스 바 초기화
    elements.ttsProgressBar.style.width = '0%';

    // 프로그레스 바 애니메이션
    const startTime = Date.now();
    ttsProgressInterval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min((elapsed / estimatedDuration) * 100, 100);
        elements.ttsProgressBar.style.width = `${progress}%`;

        if (progress >= 100) {
            clearInterval(ttsProgressInterval);
            ttsProgressInterval = null;
        }
    }, 50);
}

function hideTTSIndicator() {
    // 표시 요소 숨기기
    elements.ttsPlayingIndicator.style.display = 'none';
    elements.speakerBtn.classList.remove('playing');

    // 프로그레스 바 인터벌 정리
    if (ttsProgressInterval) {
        clearInterval(ttsProgressInterval);
        ttsProgressInterval = null;
    }

    // 프로그레스 바 초기화
    elements.ttsProgressBar.style.width = '0%';
}

// ============ TTS 설정 관리 ============
function updateTtsRateValue() {
    const value = parseFloat(elements.ttsRate.value).toFixed(1);
    elements.ttsRateValue.textContent = `${value}x`;
    TTS_CONFIG.rate = parseFloat(value);
}

function updateTtsPitchValue() {
    const value = parseFloat(elements.ttsPitch.value).toFixed(1);
    elements.ttsPitchValue.textContent = value;
    TTS_CONFIG.pitch = parseFloat(value);
}

function updateTtsVolumeValue() {
    const value = parseFloat(elements.ttsVolume.value);
    elements.ttsVolumeValue.textContent = `${Math.round(value * 100)}%`;
    TTS_CONFIG.volume = value;
}

function updateTtsNeonValue() {
    const value = parseInt(elements.ttsNeon.value);
    elements.ttsNeonValue.textContent = `${value}ms`;
    TTS_CONFIG.minNeonDuration = value;
}

async function loadTtsSettings() {
    try {
        const response = await apiCall('/settings/tts');
        if (response.success && response.tts) {
            const tts = response.tts;

            // 슬라이더 값 설정
            elements.ttsRate.value = tts.rate || 1.0;
            elements.ttsPitch.value = tts.pitch || 1.0;
            elements.ttsVolume.value = tts.volume || 1.0;
            elements.ttsNeon.value = tts.minNeonDuration || 500;

            // 표시값 업데이트 및 TTS_CONFIG 동기화
            updateTtsRateValue();
            updateTtsPitchValue();
            updateTtsVolumeValue();
            updateTtsNeonValue();

            console.log('TTS 설정 로드 완료:', tts);
        }
    } catch (error) {
        console.error('TTS 설정 로드 실패:', error);
    }
}

async function saveTtsSettings() {
    try {
        const ttsConfig = {
            rate: parseFloat(elements.ttsRate.value),
            pitch: parseFloat(elements.ttsPitch.value),
            volume: parseFloat(elements.ttsVolume.value),
            minNeonDuration: parseInt(elements.ttsNeon.value)
        };

        const response = await apiCall('/settings/tts', {
            method: 'POST',
            body: JSON.stringify(ttsConfig)
        });

        if (response.success) {
            console.log('TTS 설정 저장 완료:', ttsConfig);
            // TTS_CONFIG 업데이트
            TTS_CONFIG.rate = ttsConfig.rate;
            TTS_CONFIG.pitch = ttsConfig.pitch;
            TTS_CONFIG.volume = ttsConfig.volume;
            TTS_CONFIG.minNeonDuration = ttsConfig.minNeonDuration;
        }
    } catch (error) {
        console.error('TTS 설정 저장 실패:', error);
    }
}

// ============ 폰트 설정 관리 ============
function updateFontCategoryValue() {
    const value = parseInt(elements.fontCategory.value);
    elements.fontCategoryValue.textContent = `${value}px`;
    applyFontSizes();
}

function updateFontQuestionValue() {
    const value = parseInt(elements.fontQuestion.value);
    elements.fontQuestionValue.textContent = `${value}px`;
    applyFontSizes();
}

function updateFontAnswerValue() {
    const value = parseInt(elements.fontAnswer.value);
    elements.fontAnswerValue.textContent = `${value}px`;
    applyFontSizes();
}

function applyFontSizes() {
    // 폰트 종류
    const fontFamily = elements.fontFamily.value;

    // 대주제 (카테고리)
    const categorySize = parseInt(elements.fontCategory.value);
    elements.categoryLabel.style.fontSize = `${categorySize}px`;
    elements.categoryLabel.style.fontFamily = fontFamily;

    // 문제
    const questionSize = parseInt(elements.fontQuestion.value);
    elements.questionText.style.fontSize = `${questionSize}px`;
    elements.questionText.style.fontFamily = fontFamily;

    // 답 (옵션 버튼의 텍스트 부분 및 주관식 입력)
    const answerSize = parseInt(elements.fontAnswer.value);
    const optionButtons = document.querySelectorAll('.option-button > span:not(.option-number)');
    optionButtons.forEach(span => {
        span.style.fontSize = `${answerSize}px`;
        span.style.fontFamily = fontFamily;
    });
    elements.subjectiveInput.style.fontSize = `${answerSize}px`;
    elements.subjectiveInput.style.fontFamily = fontFamily;
}

async function loadFontSettings() {
    try {
        const response = await apiCall('/settings/fonts');
        if (response.success && response.fonts) {
            const fonts = response.fonts;

            // 폰트 종류 설정
            elements.fontFamily.value = fonts.fontFamily || 'system-ui';

            // 슬라이더 값 설정
            elements.fontCategory.value = fonts.categorySize || 18;
            elements.fontQuestion.value = fonts.questionSize || 64;
            elements.fontAnswer.value = fonts.answerSize || 20;

            // 표시값 업데이트
            updateFontCategoryValue();
            updateFontQuestionValue();
            updateFontAnswerValue();

            // 폰트 적용
            applyFontSizes();

            console.log('폰트 설정 로드 완료:', fonts);
        }
    } catch (error) {
        console.error('폰트 설정 로드 실패:', error);
    }
}

async function saveFontSettings() {
    try {
        const fontConfig = {
            fontFamily: elements.fontFamily.value,
            categorySize: parseInt(elements.fontCategory.value),
            questionSize: parseInt(elements.fontQuestion.value),
            answerSize: parseInt(elements.fontAnswer.value)
        };

        const response = await apiCall('/settings/fonts', {
            method: 'POST',
            body: JSON.stringify(fontConfig)
        });

        if (response.success) {
            console.log('폰트 설정 저장 완료:', fontConfig);
            // 폰트 적용
            applyFontSizes();
        }
    } catch (error) {
        console.error('폰트 설정 저장 실패:', error);
    }
}

// ============ 시스템 설정 관리 ============
function updateNextQuestionDelayValue() {
    const value = parseInt(elements.nextQuestionDelay.value);
    elements.nextQuestionDelayValue.textContent = `${value}ms`;
    systemSettings.nextQuestionDelay = value;
}

async function loadSystemSettings() {
    try {
        const response = await apiCall('/settings/system');
        if (response.success && response.system) {
            const system = response.system;

            // 다음 문제 딜레이
            elements.nextQuestionDelay.value = system.nextQuestionDelay || 1500;
            updateNextQuestionDelayValue();

            // 단축키
            if (system.shortcuts) {
                elements.shortcutTTS.value = system.shortcuts.tts || 'S';
                elements.shortcutLLM.value = system.shortcuts.llm || 'L';
                elements.shortcutReload.value = system.shortcuts.reload || 'R';
                elements.shortcutSettings.value = system.shortcuts.settings || ',';

                // systemSettings 업데이트
                systemSettings.shortcuts = {
                    tts: system.shortcuts.tts || 'S',
                    llm: system.shortcuts.llm || 'L',
                    reload: system.shortcuts.reload || 'R',
                    settings: system.shortcuts.settings || ',',
                    exit: 'Escape'
                };
            }

            console.log('시스템 설정 로드 완료:', system);
        }
    } catch (error) {
        console.error('시스템 설정 로드 실패:', error);
    }
}

async function saveSystemSettings() {
    try {
        const systemConfig = {
            nextQuestionDelay: parseInt(elements.nextQuestionDelay.value),
            shortcuts: {
                tts: elements.shortcutTTS.value.toUpperCase() || 'S',
                llm: elements.shortcutLLM.value.toUpperCase() || 'L',
                reload: elements.shortcutReload.value.toUpperCase() || 'R',
                settings: elements.shortcutSettings.value || ',',
                exit: 'Escape'
            }
        };

        const response = await apiCall('/settings/system', {
            method: 'POST',
            body: JSON.stringify(systemConfig)
        });

        if (response.success) {
            console.log('시스템 설정 저장 완료:', systemConfig);
            // systemSettings 업데이트
            systemSettings.nextQuestionDelay = systemConfig.nextQuestionDelay;
            systemSettings.shortcuts = systemConfig.shortcuts;
        }
    } catch (error) {
        console.error('시스템 설정 저장 실패:', error);
    }
}

// ============ 설정 관리 ============
async function loadSettings() {
    try {
        const response = await apiCall('/settings/');
        if (response.success) {
            populateSettings(response.settings);
        }
    } catch (error) {
        console.error('설정 로드 실패:', error);
    }

    // TTS 설정도 로드
    await loadTtsSettings();

    // 폰트 설정도 로드
    await loadFontSettings();

    // 시스템 설정도 로드
    await loadSystemSettings();
}

async function loadAvailableFiles() {
    try {
        const response = await apiCall('/quiz/files');
        if (response.success) {
            const select = document.getElementById('jsonFileSelect');
            select.innerHTML = response.files.map(file =>
                `<option value="${file}" ${file === response.current_file ? 'selected' : ''}>${file}</option>`
            ).join('');

            // 기존 이벤트 리스너 제거 후 새로 등록 (중복 방지)
            const newSelect = select.cloneNode(true);
            select.parentNode.replaceChild(newSelect, select);

            // JSON 파일 변경 시 해당 파일의 주제만 미리보기
            newSelect.addEventListener('change', async (e) => {
                await previewFileCategories(e.target.value);
            });
        }
    } catch (error) {
        console.error('파일 목록 로드 실패:', error);
    }
}

async function previewFileCategories(filename) {
    try {
        // 선택한 파일의 카테고리를 임시로 불러오기
        const response = await apiCall(`/quiz/load-file?filename=${filename}`, { method: 'POST' });

        if (response.success) {
            // 감지된 언어로 자동 설정
            if (response.detected_languages) {
                const { language1, language2 } = response.detected_languages;

                const lang1Select = document.getElementById('language1');
                const lang2Select = document.getElementById('language2');

                if (lang1Select) {
                    lang1Select.value = language1;
                }

                if (lang2Select) {
                    lang2Select.value = language2;
                }

                console.log(`✓ 언어 자동 감지: ${language1} → ${language2}`);
            }

            // 카테고리 다시 로드 (새 파일의 카테고리)
            const categoriesResponse = await apiCall('/settings/categories');

            if (categoriesResponse.success) {
                const container = document.getElementById('categoryCheckboxes');
                // 전체 선택 상태로 표시 (새 파일 미리보기)
                container.innerHTML = categoriesResponse.categories.map(cat => `
                    <label class="checkbox-label">
                        <input type="checkbox" name="category" value="${cat}" checked>
                        <span>${cat}</span>
                    </label>
                `).join('');

                // 카테고리 현재값 업데이트
                const categoryCurrent = document.getElementById('category-current');
                if (categoryCurrent) {
                    categoryCurrent.textContent = categoriesResponse.categories.join(', ');
                }
            }
        }
    } catch (error) {
        console.error('파일 미리보기 실패:', error);
        showCustomAlert('파일을 불러오는 중 오류가 발생했습니다.');
    }
}

function populateSettings(settings) {
    // 언어 설정
    document.getElementById('language1').value = settings.language1 || 'en';
    document.getElementById('language2').value = settings.language2 || 'ja';

    // 출제 패턴
    const pattern = settings.question_pattern || 'random';
    const patternId = `pattern_${pattern.replace('>', '_')}`;
    const patternElement = document.getElementById(patternId);
    if (patternElement) {
        patternElement.checked = true;
    }

    // 출제 패턴 현재값 표시
    const patternCurrent = document.getElementById('pattern-current');
    if (patternCurrent) {
        patternCurrent.textContent = pattern === 'random' ? '무작위' : pattern;
    }

    // 문제 유형
    const quizTypes = [];
    document.querySelectorAll('[name="quiz_type_checkbox"]').forEach(cb => {
        cb.checked = settings.quiz_types?.[cb.value] || false;
        if (cb.checked) {
            quizTypes.push(cb.value === 'subjective' ? '주관식' : '객관식');
        }
    });

    // 문제 유형 현재값 표시
    const quizTypeCurrent = document.getElementById('quiz-type-current');
    if (quizTypeCurrent) {
        quizTypeCurrent.textContent = quizTypes.join(', ') || '-';
    }

    // 출제 순서
    const orderMode = settings.order_mode || 'random';
    const orderElement = document.getElementById(`order_${orderMode}`);
    if (orderElement) {
        orderElement.checked = true;
    }

    // 출제 순서 현재값 표시
    const orderCurrent = document.getElementById('order-current');
    if (orderCurrent) {
        const orderText = orderMode === 'random' ? '무작위' : orderMode === 'forward' ? '정순' : '역순';
        orderCurrent.textContent = orderText;
    }

    // 카테고리 로드
    loadCategories(settings.selected_categories || []);

    // 카테고리 현재값 표시
    const categoryCurrent = document.getElementById('category-current');
    if (categoryCurrent) {
        const categories = settings.selected_categories || [];
        categoryCurrent.textContent = categories.length > 0 ? categories.join(', ') : '-';
    }
}

async function loadCategories(selectedCategories = []) {
    try {
        const response = await apiCall('/settings/categories');
        if (response.success) {
            const container = document.getElementById('categoryCheckboxes');
            container.innerHTML = response.categories.map(cat => `
                <label class="checkbox-label">
                    <input type="checkbox" name="category" value="${cat}" ${selectedCategories.includes(cat) ? 'checked' : ''}>
                    <span>${cat}</span>
                </label>
            `).join('');
        }
    } catch (error) {
        console.error('카테고리 로드 실패:', error);
    }
}

async function saveSettings() {
    try {
        // 1. 검증: 출제 패턴 선택 확인
        const selectedPattern = document.querySelector('[name="pattern_mode"]:checked');
        if (!selectedPattern) {
            showCustomAlert('출제 패턴을 선택해주세요.');
            return;
        }

        const pattern = selectedPattern.value;

        // 2. 검증: 문제 유형 최소 1개 이상 선택
        const quizTypesChecked = [
            document.querySelector('[name="quiz_type_checkbox"][value="subjective"]')?.checked,
            document.querySelector('[name="quiz_type_checkbox"][value="multiple_choice"]')?.checked
        ].some(checked => checked);

        if (!quizTypesChecked) {
            showCustomAlert('문제 유형을 최소 1개 이상 선택해주세요.');
            return;
        }

        // 3. 검증: 출제 순서 선택 확인
        const selectedOrder = document.querySelector('[name="order_mode"]:checked');
        if (!selectedOrder) {
            showCustomAlert('출제 순서를 선택해주세요.');
            return;
        }

        // 4. 검증: 주제(카테고리) 최소 1개 이상 선택
        const selectedCategories = Array.from(document.querySelectorAll('[name="category"]:checked')).map(cb => cb.value);
        if (selectedCategories.length === 0) {
            showCustomAlert('주제를 최소 1개 이상 선택해주세요.');
            return;
        }

        // 선택된 JSON 파일 가져오기
        const selectedFile = document.getElementById('jsonFileSelect')?.value;

        const settings = {
            quiz_file: selectedFile || 'quiz',
            language1: document.getElementById('language1').value,
            language2: document.getElementById('language2').value,
            question_pattern: pattern,
            random_patterns: {
                // 무작위 선택 시 자동으로 A>B, B>A 둘 다 포함
                "A>B": pattern === 'random',
                "B>A": pattern === 'random'
            },
            quiz_type: "random",
            quiz_types: {
                subjective: document.querySelector('[name="quiz_type_checkbox"][value="subjective"]')?.checked || false,
                multiple_choice: document.querySelector('[name="quiz_type_checkbox"][value="multiple_choice"]')?.checked || false
            },
            order_mode: selectedOrder.value,
            selected_categories: selectedCategories
        };

        // 설정 저장
        const response = await apiCall('/settings/', {
            method: 'POST',
            body: JSON.stringify(settings)
        });

        if (response.success) {
            // TTS 설정도 저장
            await saveTtsSettings();

            // 폰트 설정도 저장
            await saveFontSettings();

            // 시스템 설정도 저장
            await saveSystemSettings();

            // 설정이 성공적으로 저장되면 페이지 새로고침
            // 새로고침 전에 플래그 설정
            sessionStorage.setItem('settings_saved', 'true');
            // 새로고침 시 통계가 자동으로 초기화되고 새 설정으로 문제 로드
            window.location.reload();
        }
    } catch (error) {
        showCustomAlert(`설정 저장 실패: ${error.message}`);
    }
}

// ============ UI 유틸리티 ============
function showLoading(show) {
    elements.loading.style.display = show ? 'flex' : 'none';
    elements.quizCard.style.display = show ? 'none' : 'block';
}

function showError(message) {
    elements.questionText.textContent = `❌ ${message}`;
    elements.optionsGrid.style.display = 'none';
    elements.subjectiveContainer.style.display = 'none';
}

function showToast(message, duration = 1500) {
    const toast = document.getElementById('refreshToast');
    if (!toast) return;

    // 메시지 업데이트
    toast.textContent = message;

    // 토스트 표시
    toast.classList.add('show');

    // 지정된 시간 후 숨김
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

async function openSettings() {
    // 설정을 열 때 현재 설정을 다시 로드 (취소 시 복원용)
    const currentSettings = await apiCall('/settings/');
    originalQuizFile = currentSettings.settings?.quiz_file;  // 원래 파일 저장

    // 현재 폰트 설정 저장 (취소 시 복원용)
    originalFontSettings = {
        fontFamily: elements.fontFamily.value,
        categorySize: parseInt(elements.fontCategory.value),
        questionSize: parseInt(elements.fontQuestion.value),
        answerSize: parseInt(elements.fontAnswer.value)
    };

    await loadSettings();
    await loadAvailableFiles();
    elements.settingsModal.classList.add('active');
    elements.settingsModal.style.display = 'flex';
}

async function closeSettings() {
    // 파일이 변경되었는데 저장하지 않은 경우 원래 파일로 복구
    const currentFile = document.getElementById('jsonFileSelect')?.value;
    if (originalQuizFile && currentFile !== originalQuizFile) {
        await apiCall(`/quiz/load-file?filename=${originalQuizFile}`, { method: 'POST' });
        await loadSettings();  // 설정도 원래대로 복구
    }

    // 폰트 설정 원래대로 복구
    if (originalFontSettings) {
        elements.fontFamily.value = originalFontSettings.fontFamily;
        elements.fontCategory.value = originalFontSettings.categorySize;
        elements.fontQuestion.value = originalFontSettings.questionSize;
        elements.fontAnswer.value = originalFontSettings.answerSize;

        // 표시값 업데이트
        updateFontCategoryValue();
        updateFontQuestionValue();
        updateFontAnswerValue();

        // 폰트 적용
        applyFontSizes();
    }

    // 모든 섹션 접기
    document.querySelectorAll('.collapsible-section').forEach(section => {
        section.classList.add('collapsed');
    });

    elements.settingsModal.classList.remove('active');
    elements.settingsModal.style.display = 'none';
}

async function reloadData() {
    elements.reloadBtn.disabled = true;
    try {
        await apiCall('/quiz/reload', { method: 'POST' });

        // 통계 초기화
        resetStats();

        // 새 문제 로드
        loadNextQuestion();

        // 성공 알림 표시
        showToast('🔄 데이터가 새로고침되었습니다');
    } catch (error) {
        showCustomAlert(`리로드 실패: ${error.message}`);
    } finally {
        elements.reloadBtn.disabled = false;
    }
}

function toggleSection(e) {
    const section = e.currentTarget.parentElement;
    section.classList.toggle('collapsed');
}

function selectAllCategories(select) {
    document.querySelectorAll('[name="category"]').forEach(cb => {
        cb.checked = select;
    });
}

// ============ LLM 설정 관리 ============

const PERSONA_DESCRIPTIONS = {
    friendly_tutor: "친근하고 격려적인 언어 학습 도우미",
    professional_teacher: "체계적이고 상세한 설명을 제공하는 교사",
    casual_friend: "편안하고 일상적인 대화로 돕는 친구",
    native_speaker: "원어민 관점에서 자연스러운 표현을 알려주는 도우미",
    grammar_expert: "문법 규칙과 구조를 상세히 설명하는 전문가"
};

function updatePersonaDescription() {
    /**
     * 페르소나 선택에 따라 설명 업데이트
     */
    const selectedPersona = elements.llmPersona.value;
    const description = PERSONA_DESCRIPTIONS[selectedPersona] || "";
    elements.personaDescription.textContent = description;
}

function updateTemperatureValue() {
    /**
     * Temperature 슬라이더 값 표시 업데이트
     */
    const value = parseFloat(elements.llmTemperature.value).toFixed(1);
    elements.temperatureValue.textContent = value;
}

function updateMaxTokensValue() {
    /**
     * Max Tokens 슬라이더 값 표시 업데이트
     */
    const value = elements.llmMaxTokens.value;
    elements.maxTokensValue.textContent = value;
}

function toggleCustomModelInput() {
    /**
     * "직접 입력" 선택 시 커스텀 입력 필드 표시
     */
    const isCustom = elements.llmModel.value === 'custom';
    elements.llmModelCustom.style.display = isCustom ? 'block' : 'none';
}

async function checkLlmStatus() {
    /**
     * LLM 연결 상태 확인 및 표시
     */
    try {
        // LLM 설정 조회
        const config = await apiCall('/llm/config');

        // 연결 테스트
        const testResult = await apiCall('/llm/test', { method: 'POST' });

        // 상태에 따라 버튼 색상 변경
        updateLlmStatusIndicator(testResult.status);
    } catch (error) {
        // 에러 발생 시 빨간색 (연결 안됨)
        updateLlmStatusIndicator('disconnected');
    }
}

function updateLlmStatusIndicator(status) {
    /**
     * LLM 상태 표시기 업데이트
     * @param {string} status - 'connected', 'warning', 'disconnected'
     */
    const btn = elements.llmStatusBtn;

    // 기존 상태 클래스 제거
    btn.classList.remove('status-connected', 'status-warning', 'status-disconnected');

    // 새 상태 클래스 추가
    btn.classList.add(`status-${status}`);
}

async function openLlmConfig() {
    /**
     * LLM 설정 모달 열기
     */
    // 모달 먼저 표시 (빠른 반응)
    elements.llmConfigModal.classList.add('active');
    elements.llmConfigModal.style.display = 'flex';

    // 로딩 상태 표시
    updateConnectionStatus('warning', '설정 로드 중...');

    try {
        // 기존 설정 로드
        const config = await apiCall('/llm/config');

        if (config.has_config) {
            const savedModel = config.llm_model;

            // 드롭다운에 있는 모델인지 확인
            const selectOptions = Array.from(elements.llmModel.options).map(opt => opt.value);

            if (selectOptions.includes(savedModel)) {
                // 드롭다운에 있는 모델
                elements.llmModel.value = savedModel;
                elements.llmModelCustom.style.display = 'none';
            } else {
                // 커스텀 모델
                elements.llmModel.value = 'custom';
                elements.llmModelCustom.value = savedModel;
                elements.llmModelCustom.style.display = 'block';
            }

            elements.llmApiKey.value = config.api_key;

            // 프롬프트 설정 로드
            const prompts = config.prompts || {};
            elements.llmPersona.value = prompts.persona || 'friendly_tutor';
            elements.llmCustomPrompt.value = prompts.custom_system_prompt || '';
            elements.llmTemperature.value = prompts.temperature || 0.7;
            elements.llmMaxTokens.value = prompts.max_tokens || 1024;
            updatePersonaDescription();
            updateTemperatureValue();
            updateMaxTokensValue();

            // 연결 상태 표시
            const testResult = await apiCall('/llm/test', { method: 'POST' });
            updateConnectionStatus(testResult.status, testResult.message);
        } else {
            // 설정이 없으면 빈 값
            elements.llmModel.value = '';
            elements.llmModelCustom.value = '';
            elements.llmModelCustom.style.display = 'none';
            elements.llmApiKey.value = '';
            elements.llmPersona.value = 'friendly_tutor';
            elements.llmCustomPrompt.value = '';
            elements.llmTemperature.value = 0.7;
            elements.llmMaxTokens.value = 1024;
            updatePersonaDescription();
            updateTemperatureValue();
            updateMaxTokensValue();
            updateConnectionStatus('disconnected', '연결 상태를 확인하려면 저장하세요');
        }
    } catch (error) {
        console.error('LLM 설정 로드 실패:', error);
        updateConnectionStatus('disconnected', '설정 로드 실패');
    }
}

function closeLlmConfig() {
    /**
     * LLM 설정 모달 닫기
     */
    elements.llmConfigModal.classList.remove('active');
    elements.llmConfigModal.style.display = 'none';
}

async function saveLlmConfiguration() {
    /**
     * LLM 설정 저장 및 연결 테스트
     */
    try {
        const selectedModel = elements.llmModel.value;
        const apiKey = elements.llmApiKey.value.trim();

        // 실제 모델명 결정
        let llmModel;
        if (selectedModel === 'custom') {
            llmModel = elements.llmModelCustom.value.trim();
            if (!llmModel) {
                showCustomAlert('커스텀 모델명을 입력해주세요.');
                return;
            }
        } else {
            llmModel = selectedModel;
        }

        // 유효성 검사
        if (!llmModel || !apiKey) {
            showCustomAlert('LLM 모델과 API 키를 모두 입력해주세요.');
            return;
        }

        // 프롬프트 설정
        const persona = elements.llmPersona.value;
        const customPrompt = elements.llmCustomPrompt.value.trim();
        const temperature = parseFloat(elements.llmTemperature.value);
        const maxTokens = parseInt(elements.llmMaxTokens.value);

        // 전체 설정 저장
        const saveResult = await apiCall('/llm/config/full', {
            method: 'POST',
            body: JSON.stringify({
                llm_model: llmModel,
                api_key: apiKey,
                prompts: {
                    persona: persona,
                    custom_system_prompt: customPrompt,
                    temperature: temperature,
                    max_tokens: maxTokens
                }
            })
        });

        if (saveResult.success) {
            // 연결 테스트
            const testResult = await apiCall('/llm/test', { method: 'POST' });

            // 상태 업데이트
            updateConnectionStatus(testResult.status, testResult.message);
            updateLlmStatusIndicator(testResult.status);

            // 성공 메시지
            showToast('✅ LLM 설정이 저장되었습니다');

            // 0.5초 후 모달 닫기
            setTimeout(() => {
                closeLlmConfig();
            }, 500);
        }
    } catch (error) {
        showCustomAlert(`LLM 설정 저장 실패: ${error.message}`);
        updateConnectionStatus('warning', `저장 실패: ${error.message}`);
    }
}

function updateConnectionStatus(status, message) {
    /**
     * LLM 연결 상태 표시 업데이트
     * @param {string} status - 'connected', 'warning', 'disconnected'
     * @param {string} message - 상태 메시지
     */
    const statusEl = elements.llmConnectionStatus;
    const textEl = statusEl.querySelector('.status-text');

    // 기존 상태 클래스 제거
    statusEl.classList.remove('status-connected', 'status-warning', 'status-disconnected');

    // 새 상태 클래스 추가
    statusEl.classList.add(`status-${status}`);

    // 메시지 업데이트
    textEl.textContent = message;
}

// ============ LLM 질문 기능 ============

function openLlmHelp() {
    /**
     * LLM 질문 모달 열기 (전구 버튼 클릭)
     */
    // 현재 문제 정보 가져오기
    const category = currentQuestion?.category || '주제';
    const questionText = currentQuestion?.question || '문제';

    // 동적 플레이스홀더 생성
    const placeholder = `${category}의 "${questionText}"가 뭐야??`;

    // 플레이스홀더 설정
    elements.llmQuestionInput.placeholder = placeholder;

    // 입력 필드 초기화 (이전 질문 유지하지 않음)
    elements.llmQuestionInput.value = '';

    // 채팅 메시지 영역에 환영 메시지 표시 (이미 메시지가 있으면 초기화하지 않음)
    if (elements.llmChatMessages.children.length === 0) {
        elements.llmChatMessages.innerHTML = `
            <div class="llm-welcome-message">
                <div class="llm-avatar-large">💡</div>
                <h3>안녕하세요! AI 학습 도우미입니다</h3>
                <p>궁금한 점을 자유롭게 물어보세요</p>
            </div>
        `;
    }

    // 모달 열기
    elements.llmModal.classList.add('active');
    elements.llmModal.style.display = 'flex';

    // 입력 필드에 포커스
    setTimeout(() => elements.llmQuestionInput.focus(), 100);
}

function closeLlmHelp() {
    /**
     * LLM 질문 모달 닫기
     */
    elements.llmModal.classList.remove('active');
    elements.llmModal.style.display = 'none';
}

function clearLlmChat() {
    /**
     * LLM 채팅 기록 삭제
     */
        elements.llmChatMessages.innerHTML = `
            <div class="llm-welcome-message">
                <div class="llm-avatar-large">💡</div>
                <h3>안녕하세요! AI 학습 도우미입니다</h3>
                <p>궁금한 점을 자유롭게 물어보세요</p>
            </div>
        `;
        showToast('🗑️ 채팅 기록이 삭제되었습니다');

}

function createChatMessage(text, isUser = false) {
    /**
     * 채팅 메시지 버블 생성
     * @param {string} text - 메시지 내용
     * @param {boolean} isUser - 사용자 메시지 여부
     * @returns {HTMLElement} 메시지 요소
     */
    const messageDiv = document.createElement('div');
    messageDiv.className = `llm-message ${isUser ? 'user' : 'assistant'}`;

    const avatarSpan = document.createElement('span');
    avatarSpan.className = 'llm-message-avatar';
    avatarSpan.textContent = isUser ? '👤' : '💡';

    const contentWrapper = document.createElement('div');
    contentWrapper.style.display = 'flex';
    contentWrapper.style.flexDirection = 'column';
    contentWrapper.style.gap = '4px';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'llm-message-content';
    contentDiv.textContent = text;

    // 시간 표시
    const timeDiv = document.createElement('div');
    timeDiv.className = 'llm-message-time';
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    timeDiv.textContent = `${hours}:${minutes}`;

    // 더블클릭으로 클립보드 복사
    contentDiv.addEventListener('dblclick', async () => {
        try {
            await navigator.clipboard.writeText(text);
            contentDiv.classList.add('copied');
            showToast('📋 클립보드에 복사되었습니다', 1000);
            setTimeout(() => {
                contentDiv.classList.remove('copied');
            }, 500);
        } catch (error) {
            console.error('클립보드 복사 실패:', error);
            showToast('❌ 복사 실패', 1000);
        }
    });

    contentWrapper.appendChild(contentDiv);
    contentWrapper.appendChild(timeDiv);

    messageDiv.appendChild(avatarSpan);
    messageDiv.appendChild(contentWrapper);

    return messageDiv;
}

function createTypingIndicator() {
    /**
     * 타이핑 인디케이터 생성
     * @returns {HTMLElement} 타이핑 인디케이터 요소
     */
    const messageDiv = document.createElement('div');
    messageDiv.className = 'llm-message assistant typing-indicator';
    messageDiv.id = 'llmTypingIndicator';

    const avatarSpan = document.createElement('span');
    avatarSpan.className = 'llm-message-avatar';
    avatarSpan.textContent = '💡';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'llm-message-content';

    const dotsDiv = document.createElement('div');
    dotsDiv.className = 'typing-dots';
    dotsDiv.innerHTML = '<span></span><span></span><span></span>';

    contentDiv.appendChild(dotsDiv);
    messageDiv.appendChild(avatarSpan);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
}

function scrollChatToBottom() {
    /**
     * 채팅 메시지 영역을 맨 아래로 스크롤
     */
    elements.llmChatMessages.scrollTop = elements.llmChatMessages.scrollHeight;
}

async function sendLlmQuestion() {
    /**
     * LLM에게 질문 전송 및 답변 받기 (SSE 스트리밍)
     */
    const question = elements.llmQuestionInput.value.trim();
    if (!question) return;

    const welcomeMessage = elements.llmChatMessages.querySelector('.llm-welcome-message');
    if (welcomeMessage) welcomeMessage.remove();

    const userMessage = createChatMessage(question, true);
    elements.llmChatMessages.appendChild(userMessage);

    elements.llmQuestionInput.value = '';
    elements.llmQuestionInput.style.height = 'auto';
    scrollChatToBottom();

    const typingIndicator = createTypingIndicator();
    elements.llmChatMessages.appendChild(typingIndicator);
    scrollChatToBottom();

    elements.llmSendBtn.disabled = true;
    elements.llmQuestionInput.disabled = true;

    try {
        const context = currentQuestion ? {
            category: currentQuestion.category,
            question: currentQuestion.question,
            answer: currentQuestion.answer
        } : null;

        // SSE 스트리밍 시도
        const response = await fetch(`${API_BASE}/llm/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, context })
        });

        typingIndicator.remove();

        if (response.ok && response.headers.get('content-type')?.includes('text/event-stream')) {
            // 스트리밍 응답
            const assistantMessage = createChatMessage('', false);
            elements.llmChatMessages.appendChild(assistantMessage);
            const textEl = assistantMessage.querySelector('.llm-message-text') || assistantMessage.querySelector('p') || assistantMessage;
            let fullText = '';

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.text) {
                                fullText += data.text;
                                textEl.textContent = fullText;
                                scrollChatToBottom();
                            }
                            if (data.error) {
                                textEl.textContent = `오류: ${data.error}`;
                            }
                        } catch (e) {}
                    }
                }
            }
        } else {
            // Fallback: non-streaming
            const data = await response.json();
            if (data.success) {
                const assistantMessage = createChatMessage(data.response, false);
                elements.llmChatMessages.appendChild(assistantMessage);
            } else {
                const errorMessage = createChatMessage(`오류: ${data.error}`, false);
                elements.llmChatMessages.appendChild(errorMessage);
            }
        }
    } catch (error) {
        typingIndicator.remove();
        const errorMessage = createChatMessage(`요청 실패: ${error.message}`, false);
        elements.llmChatMessages.appendChild(errorMessage);
    } finally {
        elements.llmSendBtn.disabled = false;
        elements.llmQuestionInput.disabled = false;
        scrollChatToBottom();
        elements.llmQuestionInput.focus();
    }
}


// ============ Phase 6: 테마 전환 ============
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    let newTheme;

    if (current === 'dark') {
        newTheme = 'light';
    } else if (current === 'light') {
        newTheme = 'dark';
    } else {
        // Auto mode → toggle based on system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        newTheme = prefersDark ? 'light' : 'dark';
    }

    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('lexicon-theme', newTheme);
    showToast(`테마: ${newTheme === 'dark' ? '다크' : '라이트'} 모드`);
}

function restoreTheme() {
    const saved = localStorage.getItem('lexicon-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
    }
}


// ============ Phase 6: 학습 진도 저장/복원 ============
async function loadProgress() {
    try {
        const response = await apiCall('/quiz/progress');
        if (response.success && response.progress) {
            const p = response.progress;
            stats.total = p.total || 0;
            stats.correct = p.correct || 0;
            stats.incorrect = p.incorrect || 0;
            updateStatsDisplay();
        }
    } catch (e) {
        // 진도 복원 실패는 무시
    }
}

async function saveProgress() {
    try {
        await apiCall('/quiz/progress', {
            method: 'POST',
            body: JSON.stringify({
                total: stats.total,
                correct: stats.correct,
                incorrect: stats.incorrect
            })
        });
    } catch (e) {
        // 진도 저장 실패는 무시
    }
}

function updateStatsDisplay() {
    const accuracy = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;
    document.getElementById('headerStatTotal').textContent = stats.total;
    document.getElementById('headerStatCorrect').textContent = stats.correct;
    document.getElementById('headerStatIncorrect').textContent = stats.incorrect;
    document.getElementById('headerStatAccuracy').textContent = accuracy + '%';
}


// ============ Phase 6: 오답 복습 모드 ============
async function toggleReviewMode() {
    if (isReviewMode) {
        // 복습 모드 해제 → 원래 데이터로 복원
        isReviewMode = false;
        elements.reviewWrongBtn.style.opacity = '1';
        await apiCall('/quiz/reload', { method: 'POST' });
        showToast('일반 모드로 돌아갑니다');
        loadNextQuestion();
        return;
    }

    try {
        const response = await apiCall('/quiz/review-wrong', { method: 'POST' });
        if (response.success) {
            isReviewMode = true;
            elements.reviewWrongBtn.style.opacity = '0.5';
            showToast(response.message);
            loadNextQuestion();
        } else {
            showToast(response.message || '오답 데이터가 없습니다');
        }
    } catch (e) {
        showToast('오답 복습 모드 시작 실패');
    }
}


// ============ Phase 6: 세션 통계 저장 ============
async function saveSessionOnExit() {
    if (stats.total === 0) return;

    const duration = (Date.now() - sessionStartTime) / 1000;
    const accuracy = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) / 100 : 0;

    // 진도 저장
    try {
        navigator.sendBeacon(`${API_BASE}/quiz/progress`, JSON.stringify({
            total: stats.total,
            correct: stats.correct,
            incorrect: stats.incorrect
        }));
    } catch (e) {}

    // 세션 통계 저장
    try {
        navigator.sendBeacon(`${API_BASE}/quiz/session-stats`, JSON.stringify({
            total: stats.total,
            correct: stats.correct,
            incorrect: stats.incorrect,
            accuracy: accuracy,
            duration_seconds: duration
        }));
    } catch (e) {}
}


console.log('✅ Lexicon App 로드 완료');
