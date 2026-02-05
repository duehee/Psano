"""
전시용 Talk 페이지
- 혼잣말 주기적 표시 → 키 입력 시 해당 주제로 대화 시작
- 어두운 톤, 미니멀, 부드러운 애니메이션
- /exhibit_talk 경로로 접근
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("", response_class=HTMLResponse)
def exhibit_talk_page():
    return """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>사노 - Talk</title>
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
      max-width: 650px;
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
       성격 표시 (오른쪽 상단)
       ================== */
    .personality-panel {
      position: fixed;
      top: 30px;
      right: 30px;
      text-align: right;
    }

    .personality-title {
      font-size: 0.75rem;
      color: #444;
      margin-bottom: 10px;
      letter-spacing: 1px;
    }

    .personality-traits {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .trait {
      font-size: 0.85rem;
      font-weight: 300;
      color: #666;
      opacity: 0;
      transform: translateX(10px);
      transition: all 0.5s ease;
    }
    .trait.visible {
      opacity: 1;
      transform: translateX(0);
    }

    /* ==================
       혼잣말 화면 (Idle)
       ================== */
    .idle-screen {
      align-items: center;
      text-align: center;
      gap: 50px;
    }

    .idle-monologue {
      font-size: 1.3rem;
      font-weight: 300;
      line-height: 1.9;
      color: #aaa;
      min-height: 100px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: opacity 0.5s ease;
    }
    .idle-monologue.changing {
      opacity: 0;
    }

    .idle-hint {
      margin-top: 30px;
      font-size: 0.85rem;
      color: #444;
    }

    /* ==================
       대화 화면
       ================== */
    .chat-screen {
      gap: 30px;
      height: 70vh;
    }

    .chat-messages {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding: 10px 0;
    }

    .message {
      max-width: 85%;
      padding: 16px 20px;
      border-radius: 16px;
      font-size: 1rem;
      line-height: 1.7;
      font-weight: 300;
      opacity: 0;
      transform: translateY(10px);
      animation: messageIn 0.4s ease forwards;
    }

    @keyframes messageIn {
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .message.assistant {
      align-self: flex-start;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      color: #ddd;
    }

    .message.user {
      align-self: flex-end;
      background: #2a2a2a;
      border: 1px solid #3a3a3a;
      color: #fff;
    }

    .message.system {
      align-self: center;
      background: transparent;
      color: #666;
      font-size: 0.9rem;
      padding: 10px;
    }

    .chat-input-area {
      display: flex;
      gap: 12px;
      padding-top: 20px;
      border-top: 1px solid #1a1a1a;
    }

    .chat-input {
      flex: 1;
      padding: 16px 20px;
      font-size: 1rem;
      font-family: inherit;
      background: #111;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      color: #fff;
      transition: border-color 0.3s;
    }
    .chat-input:focus {
      outline: none;
      border-color: #444;
    }
    .chat-input::placeholder {
      color: #444;
    }
    .chat-input:disabled {
      opacity: 0.5;
    }

    .send-btn {
      padding: 16px 24px;
      font-size: 0.95rem;
      font-family: inherit;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 12px;
      color: #888;
      cursor: pointer;
      transition: all 0.3s;
    }
    .send-btn:hover:not(:disabled) {
      border-color: #444;
      color: #fff;
    }
    .send-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
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
    .typing-indicator {
      display: none;
      align-self: flex-start;
      padding: 16px 20px;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      border-radius: 16px;
    }
    .typing-indicator.show {
      display: flex;
      gap: 6px;
    }
    .typing-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #555;
      animation: typing 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
      0%, 80%, 100% { opacity: 0.3; }
      40% { opacity: 1; }
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

    /* 스크롤바 */
    .chat-messages::-webkit-scrollbar {
      width: 6px;
    }
    .chat-messages::-webkit-scrollbar-track {
      background: transparent;
    }
    .chat-messages::-webkit-scrollbar-thumb {
      background: #333;
      border-radius: 3px;
    }

    /* ==================
       오프라인/에러 표시
       ================== */
    .connection-status {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      padding: 12px 20px;
      background: #1a1a1a;
      border-bottom: 1px solid #333;
      color: #e57373;
      font-size: 0.9rem;
      text-align: center;
      transform: translateY(-100%);
      transition: transform 0.3s ease;
      z-index: 200;
    }
    .connection-status.show {
      transform: translateY(0);
    }
    .connection-status.reconnecting {
      color: #ffb74d;
    }
    .connection-status.online {
      color: #81c784;
    }

    /* 헬스 인디케이터 (왼쪽 상단 작은 점) */
    .health-indicator {
      position: fixed;
      top: 12px;
      left: 12px;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #4caf50;
      opacity: 0.6;
      z-index: 9999;
      transition: background 0.3s, opacity 0.3s;
    }
    .health-indicator.error {
      background: #f44336;
      opacity: 0.8;
    }
    .health-indicator.warning {
      background: #ff9800;
      opacity: 0.7;
    }
  </style>
</head>
<body>
  <!-- 헬스 인디케이터 (운영자용) -->
  <div class="health-indicator" id="healthIndicator" title="서버 상태: 정상"></div>

  <!-- 연결 상태 표시 -->
  <div class="connection-status" id="connectionStatus">
    네트워크 연결이 끊어졌습니다
  </div>

  <!-- 성격 표시 (오른쪽 상단) -->
  <div class="personality-panel" id="personalityPanel">
    <div class="personality-title">PSANO</div>
    <div class="personality-traits" id="personalityTraits">
      <!-- 동적으로 추가 -->
    </div>
  </div>

  <div class="container">
    <!-- 혼잣말 화면 (Idle) -->
    <div class="screen idle-screen active" id="idleScreen">
      <div class="idle-monologue" id="idleMonologue">...</div>
      <div class="idle-hint">아무 키나 누르면 이 말로 사노와 대화합니다</div>
    </div>

    <!-- 대화 화면 -->
    <div class="screen chat-screen" id="chatScreen">
      <div class="chat-messages" id="chatMessages">
        <!-- 메시지들 -->
      </div>
      <div class="typing-indicator" id="typingIndicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
      <div class="chat-input-area">
        <input type="text" class="chat-input" id="chatInput" placeholder="메시지를 입력하세요..." maxlength="200">
        <button class="send-btn" id="sendBtn" onclick="sendMessage()">전송</button>
      </div>
    </div>

    <!-- 완료 화면 -->
    <div class="screen end-screen" id="endScreen">
      <div class="end-message" id="endMessage">
        오늘 대화는 여기까지.<br>다음에 또 이야기하자.
      </div>
      <button class="restart-btn" onclick="restart()">처음으로</button>
    </div>
  </div>

  <div class="toast" id="toast"></div>

<script>
const API_BASE = '';
let sessionId = null;
let currentIdleId = null;
let currentIdleText = '';
let idleInterval = null;
let isProcessing = false;
let nudgeTimer = null;
const NUDGE_DELAY = 15000; // 15초

let autoRestartTimer = null;
const END_SCREEN_AUTO_RESTART = 30000; // 완료 화면 30초 후 자동 복귀
const IDLE_AUTO_RESTART = 120000; // 대화 중 2분 입력 없으면 자동 복귀

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
// 연결 상태 감지 & 서버 복구
// ==================

let isOnline = navigator.onLine;
let serverHealthy = true;
let healthCheckInterval = null;
const HEALTH_CHECK_INTERVAL = 5000; // 5초마다 서버 체크

function showConnectionStatus(message, className) {
  const el = document.getElementById('connectionStatus');
  el.textContent = message;
  el.className = 'connection-status show ' + (className || '');
}

function hideConnectionStatus() {
  document.getElementById('connectionStatus').classList.remove('show');
}

function updateHealthIndicator(healthy) {
  const indicator = document.getElementById('healthIndicator');
  if (healthy) {
    indicator.className = 'health-indicator';
    indicator.title = '서버 상태: 정상';
  } else {
    indicator.className = 'health-indicator error';
    indicator.title = '서버 상태: 연결 끊김';
  }
}

async function checkServerHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    const res = await fetch('/health', { signal: controller.signal });
    clearTimeout(timeoutId);
    const healthy = res.ok;
    updateHealthIndicator(healthy);
    return healthy;
  } catch (e) {
    updateHealthIndicator(false);
    return false;
  }
}

async function startHealthCheck() {
  if (healthCheckInterval) return;

  healthCheckInterval = setInterval(async () => {
    const healthy = await checkServerHealth();

    if (healthy && (!serverHealthy || !isOnline)) {
      // 서버 복구됨
      serverHealthy = true;
      isOnline = true;
      showConnectionStatus('연결이 복구되었습니다', 'online');
      setTimeout(hideConnectionStatus, 2000);

      // idle 상태면 다시 시작
      if (document.getElementById('idleScreen').classList.contains('active')) {
        startIdleLoop();
        loadPersonality();
      }
    }

    if (!healthy) {
      serverHealthy = false;
      showConnectionStatus('서버에 연결할 수 없습니다. 재연결 시도 중...', 'reconnecting');
    }
  }, HEALTH_CHECK_INTERVAL);
}

function stopHealthCheck() {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
    healthCheckInterval = null;
  }
}

// 브라우저 온라인/오프라인 이벤트
window.addEventListener('online', () => {
  isOnline = true;
  showConnectionStatus('네트워크 연결됨. 서버 확인 중...', 'reconnecting');
  startHealthCheck();
});

window.addEventListener('offline', () => {
  isOnline = false;
  serverHealthy = false;
  showConnectionStatus('네트워크 연결이 끊어졌습니다', '');
  startHealthCheck();
});

// ==================
// 화면 전환
// ==================

function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => {
    s.classList.remove('active');
  });
  document.getElementById(screenId).classList.add('active');
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

// 에러 표시 후 자동 복귀
const ERROR_AUTO_RESTART_DELAY = 3000; // 3초 후 자동 복귀

function showErrorAndRestart(msg) {
  showToast(msg + ' (자동으로 처음으로 돌아갑니다)');
  setTimeout(() => {
    restart();
  }, ERROR_AUTO_RESTART_DELAY);
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
      serverHealthy = false;
      startHealthCheck();
      throw new Error('응답 시간이 초과되었습니다');
    }
    if (e.message === 'Failed to fetch' || e.message.includes('network')) {
      serverHealthy = false;
      startHealthCheck();
      throw new Error('네트워크 연결을 확인해주세요');
    }
    throw e;
  }
}

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

function startIdleAutoRestart() {
  resetAutoRestartTimer();
  autoRestartTimer = setTimeout(async () => {
    if (!sessionId) return;

    // 세션 종료 후 idle로
    try {
      await api('/talk/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId })
      });
    } catch (e) {
      console.error('Auto restart end error:', e);
    }
    restart();
  }, IDLE_AUTO_RESTART);
}

// ==================
// 성격 표시
// ==================

// 가치축 쌍 (각 쌍에서 높은 쪽 선택)
const AXIS_PAIRS = [
  ['self_direction', 'conformity'],
  ['stimulation', 'security'],
  ['hedonism', 'tradition'],
  ['achievement', 'benevolence'],
  ['power', 'universalism']
];

// 한글 라벨
const VALUE_LABELS = {
  self_direction: '자기주도',
  conformity: '순응',
  stimulation: '자극추구',
  security: '안전',
  hedonism: '쾌락',
  tradition: '전통',
  achievement: '성취',
  benevolence: '박애',
  power: '권력',
  universalism: '보편'
};

async function loadPersonality() {
  try {
    const data = await api('/state');
    const scores = data.axis_scores || {};

    const container = document.getElementById('personalityTraits');
    container.innerHTML = '';

    // 각 쌍에서 높은 값 선택
    const traits = [];
    for (const [a, b] of AXIS_PAIRS) {
      const scoreA = scores[a] || 0;
      const scoreB = scores[b] || 0;
      const winner = scoreA >= scoreB ? a : b;
      traits.push(winner);
    }

    // 표시
    for (let i = 0; i < traits.length; i++) {
      const trait = traits[i];
      const div = document.createElement('div');
      div.className = 'trait';
      div.textContent = VALUE_LABELS[trait] || trait;
      container.appendChild(div);

      // 순차 애니메이션
      setTimeout(() => {
        div.classList.add('visible');
      }, 200 + i * 150);
    }

  } catch (e) {
    console.error('Personality load error:', e);
  }
}

// ==================
// 혼잣말 (Idle)
// ==================

async function loadRandomMonologue() {
  try {
    const data = await api('/idle/random');
    currentIdleId = data.id;
    currentIdleText = data.text;
    return data.text;
  } catch (e) {
    console.error('Monologue error:', e);
    return '...';
  }
}

async function displayMonologue() {
  const el = document.getElementById('idleMonologue');

  // 페이드 아웃
  el.classList.add('changing');

  await new Promise(r => setTimeout(r, 500));

  const text = await loadRandomMonologue();
  el.textContent = text;

  // 페이드 인
  el.classList.remove('changing');
}

function startIdleLoop() {
  displayMonologue();
  idleInterval = setInterval(() => {
    displayMonologue();
  }, 5000);
}

function stopIdleLoop() {
  if (idleInterval) {
    clearInterval(idleInterval);
    idleInterval = null;
  }
}

// ==================
// 대화
// ==================

function addMessage(text, type) {
  const container = document.getElementById('chatMessages');
  const msg = document.createElement('div');
  msg.className = 'message ' + type;
  msg.textContent = text;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
}

function showTyping(show) {
  document.getElementById('typingIndicator').classList.toggle('show', show);
}

function setInputEnabled(enabled) {
  document.getElementById('chatInput').disabled = !enabled;
  document.getElementById('sendBtn').disabled = !enabled;
}

// ==================
// Nudge (15초 무응답 시)
// ==================

function resetNudgeTimer() {
  if (nudgeTimer) {
    clearTimeout(nudgeTimer);
    nudgeTimer = null;
  }
}

function startNudgeTimer() {
  resetNudgeTimer();
  nudgeTimer = setTimeout(async () => {
    if (!sessionId || isProcessing) return;
    await callNudge();
  }, NUDGE_DELAY);
}

async function callNudge() {
  if (isProcessing) return;

  try {
    const data = await api('/monologue/nudge', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId })
    });

    if (data.nudge_text) {
      addMessage(data.nudge_text, 'assistant');
    }

    // 한 턴에 한 번만 (사용자 응답 후 다시 시작)

  } catch (e) {
    console.error('Nudge error:', e);
  }
}

async function startTalk() {
  if (!currentIdleId) return;

  stopIdleLoop();

  try {
    // 1) 세션 시작
    const sessionData = await api('/session/start', {
      method: 'POST',
      body: JSON.stringify({ visitor_name: null })
    });
    sessionId = sessionData.session_id;

    // 2) 대화 시작
    document.getElementById('personalityPanel').style.display = 'none';
    showScreen('chatScreen');
    showTyping(true);

    const talkData = await api('/talk/start', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        idle_id: currentIdleId
      })
    });

    showTyping(false);

    // 혼잣말 표시 (시스템 메시지로)
    addMessage(currentIdleText, 'system');

    // 사노의 첫 마디
    addMessage(talkData.assistant_first_text, 'assistant');

    // Nudge 타이머 시작
    startNudgeTimer();
    // 자동 재시작 타이머 시작
    startIdleAutoRestart();

    document.getElementById('chatInput').focus();

  } catch (e) {
    showErrorAndRestart(e.message);
  }
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();

  if (!text || isProcessing) return;

  // Nudge 타이머 리셋
  resetNudgeTimer();
  // 자동 재시작 타이머 리셋
  resetAutoRestartTimer();

  isProcessing = true;
  setInputEnabled(false);

  // 사용자 메시지 표시
  addMessage(text, 'user');
  input.value = '';

  showTyping(true);

  try {
    const data = await api('/talk/turn', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        user_text: text
      })
    });

    showTyping(false);

    // 사노 응답 표시
    if (data.ui_text) {
      addMessage(data.ui_text, 'assistant');
    }

    // 종료 체크
    if (data.should_end || data.global_ended) {
      // 종료 처리
      resetNudgeTimer();
      resetAutoRestartTimer();

      try {
        await api('/talk/end', {
          method: 'POST',
          body: JSON.stringify({ session_id: sessionId })
        });
      } catch (e) {
        console.log('Talk end error:', e.message);
      }

      // 글로벌 토큰 소진 → 형성기로 이동
      if (data.global_ended) {
        // "고마웠어." 메시지가 이미 표시됨
        // 3초 후 형성기로 리다이렉트
        setTimeout(() => {
          window.location.href = '/exhibit_teach';
        }, 3000);
        return;
      }

      // 로컬 종료 → 일반 완료 화면
      setTimeout(() => {
        showScreen('endScreen');
        startEndScreenAutoRestart();
      }, 2000);
      return;
    }

    // Nudge 타이머 재시작
    startNudgeTimer();
    // 자동 재시작 타이머 재시작
    startIdleAutoRestart();

    setInputEnabled(true);
    input.focus();

  } catch (e) {
    showTyping(false);
    showErrorAndRestart(e.message);
  }

  isProcessing = false;
}

function restart() {
  sessionId = null;
  currentIdleId = null;
  currentIdleText = '';
  isProcessing = false;

  resetNudgeTimer();
  resetAutoRestartTimer();

  document.getElementById('chatMessages').innerHTML = '';
  document.getElementById('chatInput').value = '';
  setInputEnabled(true);

  document.getElementById('personalityPanel').style.display = 'block';
  showScreen('idleScreen');
  startIdleLoop();
}

// ==================
// 이벤트 핸들러
// ==================

// Idle 화면에서 아무 키 → 대화 시작
document.addEventListener('keydown', (e) => {
  if (!document.getElementById('idleScreen').classList.contains('active')) return;
  if (e.key.length > 1 && !['Enter', ' '].includes(e.key)) return;
  startTalk();
});

// 채팅 입력 엔터
document.getElementById('chatInput').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    sendMessage();
  }
});

// 타이핑 중이면 nudge/자동재시작 타이머 리셋
document.getElementById('chatInput').addEventListener('input', () => {
  if (sessionId) {
    resetNudgeTimer();
    startNudgeTimer();
    resetAutoRestartTimer();
    startIdleAutoRestart();
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

// 대화 화면에서 ESC → 세션 종료하고 처음으로
document.addEventListener('keydown', async (e) => {
  if (!document.getElementById('chatScreen').classList.contains('active')) return;
  if (e.key === 'Escape') {
    e.preventDefault();
    if (isProcessing) return;

    resetNudgeTimer();

    try {
      await api('/talk/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId })
      });
    } catch (err) {
      console.error('End session error:', err);
    }

    restart();
  }
});

// 페이지 로드
document.addEventListener('DOMContentLoaded', async () => {
  requestWakeLock();

  // 초기 연결 상태 확인
  if (!navigator.onLine) {
    isOnline = false;
    serverHealthy = false;
    showConnectionStatus('네트워크 연결이 끊어졌습니다', '');
    startHealthCheck();
  } else {
    // 서버 상태 확인
    const healthy = await checkServerHealth();
    if (!healthy) {
      serverHealthy = false;
      showConnectionStatus('서버에 연결할 수 없습니다. 재연결 시도 중...', 'reconnecting');
      startHealthCheck();
    }
  }

  loadPersonality();
  startIdleLoop();
});
</script>
</body>
</html>
"""
