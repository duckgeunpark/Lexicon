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

// ============ DOM 요소 ============
const elements = {
    loading: document.getElementById('loading'),
    quizCard: document.getElementById('quizCard'),
    questionText: document.getElementById('questionText'),
    questionImage: document.getElementById('questionImage'),
    categoryLabel: document.getElementById('categoryLabel'),
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
    llmChatMessages: document.getElementById('llmChatMessages')
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

    // 설정 로드 (UI 업데이트용)
    loadSettings();

    // LLM 상태 확인
    checkLlmStatus();

    // loadAvailableFiles()는 설정 열 때 호출 (openSettings)

    // 설정 저장 후 새로고침 시 알림 표시
    if (sessionStorage.getItem('settings_saved') === 'true') {
        showToast('✅ 설정이 저장되고 새로고침되었습니다');
        sessionStorage.removeItem('settings_saved');
    }
});

// ============ 이벤트 리스너 ============
function initEventListeners() {
    elements.settingsBtn.addEventListener('click', openSettings);
    elements.closeModal.addEventListener('click', closeSettings);
    elements.cancelBtn.addEventListener('click', closeSettings);
    elements.saveSettingsBtn.addEventListener('click', saveSettings);
    elements.reloadBtn.addEventListener('click', reloadData);
    elements.submitBtn.addEventListener('click', submitSubjectiveAnswer);

    // Enter 키로 주관식 제출
    elements.subjectiveInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitSubjectiveAnswer();
    });

    // 설정 섹션 접기/펼치기
    document.querySelectorAll('.collapsible-header').forEach(header => {
        header.addEventListener('click', toggleSection);
    });

    // 카테고리 전체 선택/해제
    document.getElementById('selectAllCategories')?.addEventListener('click', () => selectAllCategories(true));
    document.getElementById('deselectAllCategories')?.addEventListener('click', () => selectAllCategories(false));

    // 패턴 라디오 버튼 변경 시 무작위 패턴 설정 표시/숨김
    document.querySelectorAll('[name="pattern_mode"]').forEach(radio => {
        radio.addEventListener('change', toggleRandomPatternSettings);
    });

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
}

function toggleRandomPatternSettings() {
    const randomPatternSettings = document.getElementById('randomPatternSettings');
    const isRandomSelected = document.getElementById('pattern_random')?.checked;

    if (randomPatternSettings) {
        randomPatternSettings.style.display = isRandomSelected ? 'block' : 'none';
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

    options.forEach((option, index) => {
        const btn = document.createElement('button');
        btn.className = 'option-button';
        btn.textContent = option.text;
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

// ============ 답안 처리 ============
async function selectAnswer(option, index) {
    const buttons = elements.optionsGrid.querySelectorAll('.option-button');
    buttons.forEach(btn => btn.disabled = true);

    // 정답 표시
    buttons[index].classList.add(option.is_correct ? 'correct' : 'incorrect');

    if (!option.is_correct) {
        // 오답인 경우 정답 표시
        buttons.forEach((btn, i) => {
            if (currentQuestion.options[i].is_correct) {
                btn.classList.add('correct');
            }
        });

        // 오답 저장
        await saveWrongAnswer();
    }

    // 통계 업데이트
    updateStats(option.is_correct);

    // 다음 문제로
    setTimeout(loadNextQuestion, 1500);
}

async function submitSubjectiveAnswer() {
    const userAnswer = elements.subjectiveInput.value.trim();

    if (!userAnswer) {
        alert('답을 입력해주세요.');
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

            if (!isCorrect) {
                alert(`오답입니다!\n정답: ${response.correct_answer}`);
                await saveWrongAnswer();
            }

            updateStats(isCorrect);
            setTimeout(() => {
                elements.subjectiveInput.classList.remove('correct', 'incorrect');
                loadNextQuestion();
            }, 1500);
        }
    } catch (error) {
        alert(`답안 확인 실패: ${error.message}`);
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

    const accuracy = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;

    document.getElementById('headerStatTotal').textContent = stats.total;
    document.getElementById('headerStatCorrect').textContent = stats.correct;
    document.getElementById('headerStatIncorrect').textContent = stats.incorrect;
    document.getElementById('headerStatAccuracy').textContent = `${accuracy}%`;
}

// ============ 오답 저장 ============
async function saveWrongAnswer() {
    try {
        await apiCall('/quiz/save-wrong-answer', {
            method: 'POST',
            body: JSON.stringify({
                category: currentQuestion.category,
                question: currentQuestion.question,
                answer: currentQuestion.answer
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
        alert('파일을 불러오는 중 오류가 발생했습니다.');
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

    // 무작위 패턴 설정
    if (settings.random_patterns) {
        Object.entries(settings.random_patterns).forEach(([key, value]) => {
            const element = document.getElementById(`rand_pattern_${key.replace('>', '_')}`);
            if (element) {
                element.checked = value;
            }
        });
    }

    // 무작위 패턴 설정 표시/숨김
    toggleRandomPatternSettings();

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
            alert('출제 패턴을 선택해주세요.');
            return;
        }

        // 2. 검증: 무작위 패턴 선택 시 최소 1개 이상 체크
        const pattern = selectedPattern.value;
        if (pattern === 'random') {
            const randomPatternsChecked = [
                document.getElementById('rand_pattern_A_B')?.checked,
                document.getElementById('rand_pattern_B_A')?.checked,
                document.getElementById('rand_pattern_img_A')?.checked,
                document.getElementById('rand_pattern_img_B')?.checked,
                document.getElementById('rand_pattern_img_AB')?.checked
            ].some(checked => checked);

            if (!randomPatternsChecked) {
                alert('무작위 패턴을 사용하려면 최소 1개 이상의 패턴을 선택해주세요.');
                return;
            }
        }

        // 3. 검증: 문제 유형 최소 1개 이상 선택
        const quizTypesChecked = [
            document.querySelector('[name="quiz_type_checkbox"][value="subjective"]')?.checked,
            document.querySelector('[name="quiz_type_checkbox"][value="multiple_choice"]')?.checked
        ].some(checked => checked);

        if (!quizTypesChecked) {
            alert('문제 유형을 최소 1개 이상 선택해주세요.');
            return;
        }

        // 4. 검증: 출제 순서 선택 확인
        const selectedOrder = document.querySelector('[name="order_mode"]:checked');
        if (!selectedOrder) {
            alert('출제 순서를 선택해주세요.');
            return;
        }

        // 5. 검증: 주제(카테고리) 최소 1개 이상 선택
        const selectedCategories = Array.from(document.querySelectorAll('[name="category"]:checked')).map(cb => cb.value);
        if (selectedCategories.length === 0) {
            alert('주제를 최소 1개 이상 선택해주세요.');
            return;
        }

        // 선택된 JSON 파일 가져오기
        const selectedFile = document.getElementById('jsonFileSelect')?.value;

        const settings = {
            quiz_file: selectedFile || 'quiz_v2',
            language1: document.getElementById('language1').value,
            language2: document.getElementById('language2').value,
            question_pattern: pattern,
            random_patterns: {
                "A>B": document.getElementById('rand_pattern_A_B')?.checked || false,
                "B>A": document.getElementById('rand_pattern_B_A')?.checked || false,
                "img>A": document.getElementById('rand_pattern_img_A')?.checked || false,
                "img>B": document.getElementById('rand_pattern_img_B')?.checked || false,
                "img>A,B": document.getElementById('rand_pattern_img_AB')?.checked || false
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
            // 설정이 성공적으로 저장되면 페이지 새로고침
            // 새로고침 전에 플래그 설정
            sessionStorage.setItem('settings_saved', 'true');
            // 새로고침 시 통계가 자동으로 초기화되고 새 설정으로 문제 로드
            window.location.reload();
        }
    } catch (error) {
        alert(`설정 저장 실패: ${error.message}`);
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
        alert(`리로드 실패: ${error.message}`);
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
                alert('커스텀 모델명을 입력해주세요.');
                return;
            }
        } else {
            llmModel = selectedModel;
        }

        // 유효성 검사
        if (!llmModel || !apiKey) {
            alert('LLM 모델과 API 키를 모두 입력해주세요.');
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
        alert(`LLM 설정 저장 실패: ${error.message}`);
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
    if (confirm('채팅 기록을 모두 삭제하시겠습니까?')) {
        elements.llmChatMessages.innerHTML = `
            <div class="llm-welcome-message">
                <div class="llm-avatar-large">💡</div>
                <h3>안녕하세요! AI 학습 도우미입니다</h3>
                <p>궁금한 점을 자유롭게 물어보세요</p>
            </div>
        `;
        showToast('🗑️ 채팅 기록이 삭제되었습니다');
    }
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
     * LLM에게 질문 전송 및 답변 받기 (채팅 방식)
     */
    const question = elements.llmQuestionInput.value.trim();

    // 유효성 검사
    if (!question) {
        return;  // 빈 질문은 조용히 무시
    }

    // 환영 메시지 제거 (첫 번째 질문 시)
    const welcomeMessage = elements.llmChatMessages.querySelector('.llm-welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // 사용자 메시지 추가
    const userMessage = createChatMessage(question, true);
    elements.llmChatMessages.appendChild(userMessage);

    // 입력 필드 초기화
    elements.llmQuestionInput.value = '';
    elements.llmQuestionInput.style.height = 'auto';  // 높이 초기화

    // 스크롤 맨 아래로
    scrollChatToBottom();

    // 타이핑 인디케이터 표시
    const typingIndicator = createTypingIndicator();
    elements.llmChatMessages.appendChild(typingIndicator);
    scrollChatToBottom();

    // 버튼 비활성화
    elements.llmSendBtn.disabled = true;
    elements.llmQuestionInput.disabled = true;

    try {
        // 현재 문제 컨텍스트 구성
        const context = currentQuestion ? {
            category: currentQuestion.category,
            question: currentQuestion.question,
            answer: currentQuestion.answer
        } : null;

        // LLM API 호출
        const response = await apiCall('/llm/chat', {
            method: 'POST',
            body: JSON.stringify({
                question,
                context
            })
        });

        // 타이핑 인디케이터 제거
        typingIndicator.remove();

        if (response.success) {
            // AI 응답 메시지 추가
            const assistantMessage = createChatMessage(response.response, false);
            elements.llmChatMessages.appendChild(assistantMessage);
        } else {
            // 에러 메시지 추가
            const errorMessage = createChatMessage(`오류: ${response.error}`, false);
            elements.llmChatMessages.appendChild(errorMessage);
        }
    } catch (error) {
        // 타이핑 인디케이터 제거
        typingIndicator.remove();

        // 에러 메시지 추가
        const errorMessage = createChatMessage(`요청 실패: ${error.message}`, false);
        elements.llmChatMessages.appendChild(errorMessage);
    } finally {
        // 버튼 활성화
        elements.llmSendBtn.disabled = false;
        elements.llmQuestionInput.disabled = false;

        // 스크롤 맨 아래로
        scrollChatToBottom();

        // 입력 필드에 포커스
        elements.llmQuestionInput.focus();
    }
}

console.log('✅ Lexicon App 로드 완료');
