"""
전시용 형성기(Teach) 페이지
- 혼잣말 → 이름 입력 → 질문 시작
- 어두운 톤, 미니멀, 부드러운 애니메이션
- /exhibit_teach 경로로 접근
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("", response_class=HTMLResponse)
def exhibit_page():
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>사노</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500&display=swap');

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Noto Sans KR', sans-serif;
      background: #0a0a0a;
      color: #e0e0e0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .container {
      width: 100%;
      max-width: 600px;
      min-height: 80vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    /* 화면 전환 */
    .screen {
      display: none;
      opacity: 0;
      transition: opacity 0.6s ease;
    }
    .screen.active {
      display: flex;
      flex-direction: column;
      opacity: 1;
    }

    /* ==================
       혼잣말 화면 (Idle)
       ================== */
    .idle-screen {
      align-items: center;
      text-align: center;
      gap: 50px;
    }

    .idle-text-container {
      min-height: 250px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: 14px;
    }

    .idle-line {
      font-size: 1.2rem;
      font-weight: 300;
      line-height: 1.8;
      color: #888;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.8s ease;
    }
    .idle-line.visible {
      opacity: 1;
      transform: translateY(0);
      color: #ccc;
    }
    .idle-line.fading {
      opacity: 0.4;
      color: #555;
    }

    .idle-hint {
      margin-top: 30px;
      font-size: 0.85rem;
      color: #333;
      opacity: 0;
      transition: opacity 1s ease;
    }
    .idle-hint.visible {
      opacity: 1;
      color: #555;
    }

    /* ==================
       이름 입력 화면
       ================== */
    .name-screen {
      align-items: center;
      text-align: center;
      gap: 40px;
    }

    .name-prompt {
      font-size: 1.2rem;
      font-weight: 300;
      line-height: 1.9;
      color: #aaa;
    }

    .name-input-area {
      width: 100%;
      max-width: 400px;
    }

    .name-input {
      width: 100%;
      padding: 16px 24px;
      font-size: 1.1rem;
      font-family: inherit;
      background: transparent;
      border: 1px solid #333;
      border-radius: 30px;
      color: #fff;
      text-align: center;
      transition: all 0.3s;
    }
    .name-input:focus {
      outline: none;
      border-color: #555;
    }
    .name-input::placeholder {
      color: #444;
    }

    .name-hint {
      margin-top: 16px;
      font-size: 0.85rem;
      color: #444;
    }

    /* ==================
       질문 화면
       ================== */
    .question-screen {
      gap: 50px;
    }

    .progress {
      display: flex;
      justify-content: center;
      gap: 12px;
    }
    .progress-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #333;
      transition: background 0.3s;
    }
    .progress-dot.done {
      background: #666;
    }
    .progress-dot.current {
      background: #fff;
    }

    .question-text {
      font-size: 1.4rem;
      font-weight: 300;
      line-height: 1.9;
      text-align: center;
      color: #fff;
      min-height: 120px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .choices {
      display: flex;
      flex-direction: row;
      justify-content: center;
      align-items: stretch;
      gap: 30px;
    }

    .choice-btn {
      flex: 1;
      max-width: 280px;
      padding: 24px 20px;
      font-size: 1rem;
      font-family: inherit;
      font-weight: 300;
      background: transparent;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      color: #bbb;
      cursor: pointer;
      transition: all 0.3s;
      text-align: center;
      line-height: 1.6;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }
    .choice-btn:hover {
      border-color: #555;
      color: #fff;
    }
    .choice-btn.left:hover {
      transform: translateX(-5px);
    }
    .choice-btn.right:hover {
      transform: translateX(5px);
    }
    .choice-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
    .choice-btn .arrow {
      font-size: 1.5rem;
      color: #555;
      transition: color 0.3s;
      line-height: 1;
    }
    .choice-btn:hover .arrow {
      color: #fff;
    }
    .choice-btn .text {
      font-size: 1rem;
      position: relative;
      top: -2px;
    }
    /* 선택된 버튼 강조 */
    .choice-btn.selected {
      border-color: #666;
      color: #fff;
      background: rgba(255, 255, 255, 0.05);
    }
    .choice-btn.selected .arrow {
      color: #fff;
    }
    .choice-btn.selected.left {
      transform: translateX(-5px);
    }
    .choice-btn.selected.right {
      transform: translateX(5px);
    }

    /* ==================
       반응 화면
       ================== */
    .reaction-screen {
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 60px;
    }

    .reaction-text {
      font-size: 1.1rem;
      font-weight: 300;
      line-height: 1.9;
      color: #fff;
      max-width: 520px;
      word-break: keep-all;
    }

    .next-btn {
      padding: 14px 40px;
      font-size: 0.9rem;
      font-family: inherit;
      background: transparent;
      border: 1px solid #333;
      border-radius: 30px;
      color: #888;
      cursor: pointer;
      transition: all 0.3s;
    }
    .next-btn:hover {
      border-color: #666;
      color: #fff;
    }

    /* ==================
       페르소나 생성 화면
       ================== */
    .persona-screen {
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 40px;
    }

    .persona-message {
      font-size: 1.3rem;
      font-weight: 300;
      line-height: 2.2;
      color: #fff;
      max-width: 500px;
    }

    .persona-sub {
      font-size: 0.95rem;
      color: #666;
      margin-top: 10px;
    }

    /* 빛나는 효과 */
    .persona-glow {
      animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow {
      from { text-shadow: 0 0 10px rgba(255,255,255,0.1); }
      to { text-shadow: 0 0 20px rgba(255,255,255,0.3), 0 0 40px rgba(255,255,255,0.1); }
    }

    /* ==================
       완료 화면
       ================== */
    .end-screen {
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 30px;
    }

    .end-message {
      font-size: 1.2rem;
      font-weight: 300;
      line-height: 2;
      color: #888;
    }

    .restart-btn {
      margin-top: 20px;
      padding: 14px 40px;
      font-size: 0.9rem;
      font-family: inherit;
      background: transparent;
      border: 1px solid #333;
      border-radius: 30px;
      color: #666;
      cursor: pointer;
      transition: all 0.3s;
    }
    .restart-btn:hover {
      border-color: #555;
      color: #aaa;
    }

    /* ==================
       로딩
       ================== */
    .loading {
      display: none;
      justify-content: center;
      padding: 40px;
    }
    .loading.show {
      display: flex;
    }
    .loading-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #444;
      margin: 0 4px;
      animation: pulse 1.4s infinite ease-in-out;
    }
    .loading-dot:nth-child(1) { animation-delay: 0s; }
    .loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .loading-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes pulse {
      0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
      40% { opacity: 1; transform: scale(1); }
    }

    /* ==================
       애니메이션
       ================== */
    .fade-in {
      animation: fadeIn 0.6s ease forwards;
    }
    .fade-out {
      animation: fadeOut 0.4s ease forwards;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }

    /* ==================
       토스트
       ================== */
    .toast {
      position: fixed;
      bottom: 40px;
      left: 50%;
      transform: translateX(-50%);
      padding: 14px 28px;
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 8px;
      color: #e57373;
      font-size: 0.9rem;
      opacity: 0;
      transition: opacity 0.3s;
      z-index: 100;
    }
    .toast.show {
      opacity: 1;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- 혼잣말 화면 (Idle) -->
    <div class="screen idle-screen active" id="idleScreen">
      <div class="idle-text-container" id="idleTextContainer">
        <!-- 동적으로 line 추가 -->
      </div>
      <div class="idle-hint" id="idleHint">아무 키나 누르면 대화가 시작됩니다</div>
    </div>

    <!-- 이름 입력 화면 -->
    <div class="screen name-screen" id="nameScreen">
      <div class="name-prompt">이름을 알려줄래?</div>
      <div class="name-input-area">
        <input type="text" class="name-input" id="nameInput" placeholder="이름" maxlength="20">
        <div class="name-hint">엔터를 누르면 시작됩니다</div>
      </div>
    </div>

    <!-- 질문 화면 -->
    <div class="screen question-screen" id="questionScreen">
      <div class="progress" id="progress"></div>
      <div class="question-text" id="questionText"></div>
      <div class="choices">
        <button class="choice-btn left" id="choiceA" onclick="sendAnswer('A')">
          <span class="arrow">←</span>
          <span class="text" id="choiceAText"></span>
        </button>
        <button class="choice-btn right" id="choiceB" onclick="sendAnswer('B')">
          <span class="arrow">→</span>
          <span class="text" id="choiceBText"></span>
        </button>
      </div>
      <div class="loading" id="loadingQuestion">
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
      </div>
    </div>

    <!-- 반응 화면 -->
    <div class="screen reaction-screen" id="reactionScreen">
      <div class="reaction-text" id="reactionText"></div>
      <button class="next-btn" id="nextBtn" onclick="nextQuestion()">다음</button>
    </div>

    <!-- 페르소나 생성 화면 -->
    <div class="screen persona-screen" id="personaScreen">
      <div class="persona-message persona-glow">
        이제 알 것 같아.<br>
        나는 누구인지.<br>
        <br>
        이제 너와 대화할 수 있을 것 같아.
      </div>
      <div class="persona-sub">사노의 인격이 형성되었습니다</div>
    </div>

    <!-- 완료 화면 -->
    <div class="screen end-screen" id="endScreen">
      <div class="end-message" id="endMessage">
        오늘은 여기까지.<br>다음에 또 와줘.
      </div>
      <button class="restart-btn" onclick="restart()">처음으로</button>
    </div>
  </div>

  <div class="toast" id="toast"></div>

<script>
const API_BASE = '';
let sessionId = null;
let currentQuestionId = null;
let questionIndex = 0;
const TOTAL_QUESTIONS = 5;

let idleClickable = false;

let autoRestartTimer = null;
const END_SCREEN_AUTO_RESTART = 30000; // 완료 화면 30초 후 자동 복귀
const INACTIVE_AUTO_RESTART = 60000; // 1분 입력 없으면 자동 복귀

// ==================
// 화면 꺼짐 방지 (Wake Lock)
// ==================

let wakeLock = null;

async function requestWakeLock() {
  if ('wakeLock' in navigator) {
    try {
      wakeLock = await navigator.wakeLock.request('screen');
      console.log('Wake Lock 활성화');
      wakeLock.addEventListener('release', () => {
        console.log('Wake Lock 해제됨');
      });
    } catch (e) {
      console.log('Wake Lock 실패:', e.message);
    }
  }
}

// 페이지 다시 보일 때 Wake Lock 재요청
document.addEventListener('visibilitychange', async () => {
  if (document.visibilityState === 'visible' && !wakeLock) {
    await requestWakeLock();
  }
});

// ==================
// 풀스크린 모드
// ==================

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(e => {
      console.log('Fullscreen 실패:', e.message);
    });
  } else {
    document.exitFullscreen();
  }
}

// F11로 풀스크린 토글
document.addEventListener('keydown', (e) => {
  if (e.key === 'F11') {
    e.preventDefault();
    toggleFullscreen();
  }
});

// ==================
// 자동 재시작
// ==================

function resetAutoRestartTimer() {
  if (autoRestartTimer) {
    clearTimeout(autoRestartTimer);
    autoRestartTimer = null;
  }
}

function startEndScreenAutoRestart() {
  resetAutoRestartTimer();
  autoRestartTimer = setTimeout(() => {
    restart();
  }, END_SCREEN_AUTO_RESTART);
}

function startInactiveAutoRestart() {
  resetAutoRestartTimer();
  autoRestartTimer = setTimeout(async () => {
    if (!sessionId) return;

    // 세션 종료 후 idle로
    try {
      await api('/session/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, reason: 'timeout' })
      });
    } catch (e) {
      console.error('Auto restart end error:', e);
    }
    restart();
  }, INACTIVE_AUTO_RESTART);
}

// ==================
// 화면 전환
// ==================

function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.remove('active', 'fade-in');
  });
  const screen = document.getElementById(screenId);
  screen.classList.add('active', 'fade-in');
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

function updateProgress() {
  const progress = document.getElementById('progress');
  progress.innerHTML = '';
  for (let i = 0; i < TOTAL_QUESTIONS; i++) {
    const dot = document.createElement('div');
    dot.className = 'progress-dot';
    if (i < questionIndex) dot.classList.add('done');
    if (i === questionIndex) dot.classList.add('current');
    progress.appendChild(dot);
  }
}

// ==================
// API
// ==================

const API_TIMEOUT = 20000; // 20초 (서버 LLM 8초 + 재시도 여유)

async function api(endpoint, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const res = await fetch(API_BASE + endpoint, {
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      ...options
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || '요청 실패');
    }
    return res.json();
  } catch (e) {
    clearTimeout(timeoutId);
    if (e.name === 'AbortError') {
      throw new Error('응답 시간이 초과되었습니다');
    }
    if (e.message === 'Failed to fetch' || e.message.includes('network')) {
      throw new Error('네트워크 연결을 확인해주세요');
    }
    throw e;
  }
}

// ==================
// 혼잣말 (Idle)
// ==================

async function loadGreeting() {
  try {
    const data = await api('/idle/greeting');
    const greeting = data.greeting || '';
    // 줄바꿈으로 분리
    const lines = greeting.split('\\n').filter(s => s.trim());
    return lines;
  } catch (e) {
    console.error('Greeting error:', e);
    return ['...'];
  }
}

function clearIdleLines() {
  const container = document.getElementById('idleTextContainer');
  container.innerHTML = '';
}

async function displayGreeting() {
  clearIdleLines();
  idleClickable = false;

  const lines = await loadGreeting();
  const container = document.getElementById('idleTextContainer');

  // 동적으로 line 요소 생성
  for (let i = 0; i < lines.length; i++) {
    const div = document.createElement('div');
    div.className = 'idle-line';
    div.id = 'line' + i;
    container.appendChild(div);
  }

  // 한 줄씩 순차적으로 표시
  for (let i = 0; i < lines.length; i++) {
    await new Promise(resolve => setTimeout(resolve, i === 0 ? 500 : 1200));

    // 이전 줄들 페이딩
    for (let j = 0; j < i; j++) {
      document.getElementById('line' + j).classList.add('fading');
    }

    const el = document.getElementById('line' + i);
    el.textContent = lines[i];
    el.classList.add('visible');
  }

  // 모든 줄 표시 후 힌트 표시
  await new Promise(resolve => setTimeout(resolve, 1500));
  document.getElementById('idleHint').classList.add('visible');
  idleClickable = true;
}

// ==================
// 이름 입력 → 세션 시작
// ==================

function goToNameScreen() {
  if (!idleClickable) return;
  showScreen('nameScreen');
  setTimeout(() => {
    document.getElementById('nameInput').focus();
  }, 300);
}

async function startSession(visitorName) {
  try {
    const data = await api('/session/start', {
      method: 'POST',
      body: JSON.stringify({ visitor_name: visitorName || null })
    });
    sessionId = data.session_id;
    questionIndex = 0;
    await loadQuestion();
  } catch (e) {
    showToast(e.message);
  }
}

// ==================
// 질문 & 답변
// ==================

async function loadQuestion() {
  showScreen('questionScreen');
  updateProgress();

  const loading = document.getElementById('loadingQuestion');
  const questionText = document.getElementById('questionText');
  const choiceA = document.getElementById('choiceA');
  const choiceB = document.getElementById('choiceB');

  loading.classList.add('show');
  questionText.style.opacity = '0';
  choiceA.style.display = 'none';
  choiceB.style.display = 'none';

  try {
    const data = await api(`/question/current?session_id=${sessionId}`);
    currentQuestionId = data.id;

    loading.classList.remove('show');
    questionText.textContent = data.question_text;
    questionText.style.opacity = '1';
    document.getElementById('choiceAText').textContent = data.choice_a;
    document.getElementById('choiceBText').textContent = data.choice_b;
    choiceA.style.display = 'block';
    choiceB.style.display = 'block';
    choiceA.disabled = false;
    choiceB.disabled = false;

    // 자동 재시작 타이머 시작
    startInactiveAutoRestart();
  } catch (e) {
    loading.classList.remove('show');
    showToast(e.message);
  }
}

async function sendAnswer(choice) {
  resetAutoRestartTimer();

  const choiceA = document.getElementById('choiceA');
  const choiceB = document.getElementById('choiceB');

  // 선택한 버튼 강조
  choiceA.classList.remove('selected');
  choiceB.classList.remove('selected');
  if (choice === 'A') {
    choiceA.classList.add('selected');
  } else {
    choiceB.classList.add('selected');
  }

  choiceA.disabled = true;
  choiceB.disabled = true;

  try {
    const data = await api('/answer', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        question_id: currentQuestionId,
        choice: choice
      })
    });

    questionIndex++;

    document.getElementById('reactionText').textContent = data.assistant_reaction_text;

    if (data.session_should_end) {
      document.getElementById('nextBtn').style.display = 'none';
      showScreen('reactionScreen');

      await api('/session/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, reason: 'completed' })
      });

      // 세션 종료 후 페르소나 생성 시도
      let personaGenerated = false;
      try {
        const personaResult = await api('/persona/generate', {
          method: 'POST',
          body: JSON.stringify({ force: false })
        });
        // reused=false면 이번에 새로 생성된 것
        personaGenerated = personaResult.ok && !personaResult.reused;
      } catch (e) {
        console.log('Persona not ready yet:', e.message);
      }

      // 페르소나가 생성되었으면 특별한 화면 → exhibit_talk으로 이동
      if (personaGenerated) {
        setTimeout(() => {
          showScreen('personaScreen');
          // 페르소나 화면 8초 후 exhibit_talk으로 이동
          setTimeout(() => {
            window.location.href = '/exhibit_talk';
          }, 8000);
        }, 4000);
      } else {
        setTimeout(() => {
          showScreen('endScreen');
          startEndScreenAutoRestart();
        }, 4000);
      }
    } else {
      document.getElementById('nextBtn').style.display = 'inline-block';
      showScreen('reactionScreen');
      startInactiveAutoRestart();
    }
  } catch (e) {
    showToast(e.message);
    choiceA.disabled = false;
    choiceB.disabled = false;
  }
}

function nextQuestion() {
  resetAutoRestartTimer();
  loadQuestion();
}

function restart() {
  sessionId = null;
  currentQuestionId = null;
  questionIndex = 0;
  idleClickable = false;

  resetAutoRestartTimer();

  document.getElementById('nameInput').value = '';
  document.getElementById('idleHint').classList.remove('visible');
  showScreen('idleScreen');
  displayGreeting();
}

// ==================
// 이벤트 핸들러
// ==================

// Idle 화면에서 아무 키 → 이름 입력 화면으로
document.addEventListener('keydown', (e) => {
  // idle 화면이 active일 때만 반응
  if (!document.getElementById('idleScreen').classList.contains('active')) return;
  // 특수키 무시 (Shift, Ctrl, Alt, Meta 등)
  if (e.key.length > 1 && !['Enter', ' '].includes(e.key)) return;
  goToNameScreen();
});

// 이름 입력 후 엔터 → 세션 시작
document.getElementById('nameInput').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    const name = e.target.value.trim();
    startSession(name);
  }
});

// 질문 화면에서 방향키로 선택 (← = A, → = B)
document.addEventListener('keydown', (e) => {
  if (!document.getElementById('questionScreen').classList.contains('active')) return;

  const choiceA = document.getElementById('choiceA');
  const choiceB = document.getElementById('choiceB');

  if (choiceA.disabled) return; // 이미 선택 중

  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    sendAnswer('A');
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    sendAnswer('B');
  }
});

// 반응 화면에서 엔터 → 다음 질문
document.addEventListener('keydown', (e) => {
  if (!document.getElementById('reactionScreen').classList.contains('active')) return;
  if (e.key === 'Enter') {
    e.preventDefault();
    nextQuestion();
  }
});

// 완료 화면에서 엔터 → 처음으로
document.addEventListener('keydown', (e) => {
  if (!document.getElementById('endScreen').classList.contains('active')) return;
  if (e.key === 'Enter') {
    e.preventDefault();
    restart();
  }
});

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
  requestWakeLock();
  displayGreeting();
});
</script>
</body>
</html>
"""
