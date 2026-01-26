from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = r"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Psano Test</title>
  <style>
    :root {
      --bg: #fafafa;
      --card: #ffffff;
      --text: #1a1a2e;
      --muted: #6b7280;
      --border: #e5e7eb;
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --secondary: #f3f4f6;
      --accent: #10b981;
      --danger: #ef4444;
      --shadow: 0 4px 24px rgba(0,0,0,0.06);
      --radius: 16px;
      --radius-sm: 12px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }

    .container {
      max-width: 480px;
      margin: 0 auto;
      padding: 24px 16px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* Header */
    .header {
      text-align: center;
      margin-bottom: 24px;
    }

    .header h1 {
      font-size: 28px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .header p {
      color: var(--muted);
      font-size: 14px;
      margin-top: 4px;
    }

    /* Tabs */
    .tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      background: var(--secondary);
      padding: 6px;
      border-radius: var(--radius);
    }

    .tab {
      flex: 1;
      padding: 12px 16px;
      border: none;
      background: transparent;
      border-radius: var(--radius-sm);
      font-size: 14px;
      font-weight: 600;
      color: var(--muted);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .tab.active {
      background: var(--card);
      color: var(--primary);
      box-shadow: var(--shadow);
    }

    .tab:hover:not(.active) {
      color: var(--text);
    }

    /* Session bar */
    .session-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--card);
      border-radius: var(--radius-sm);
      border: 1px solid var(--border);
      margin-bottom: 16px;
    }

    .session-bar input {
      flex: 1;
      padding: 10px 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }

    .session-bar input:focus {
      border-color: var(--primary);
    }

    .session-bar .btn {
      padding: 10px 20px;
    }

    .session-info {
      font-size: 12px;
      color: var(--muted);
      text-align: center;
      margin-bottom: 16px;
    }

    .session-info strong {
      color: var(--primary);
    }

    /* Panel */
    .panel {
      display: none;
      flex: 1;
      flex-direction: column;
    }

    .panel.active {
      display: flex;
    }

    /* Card */
    .card {
      background: var(--card);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      overflow: hidden;
    }


    /* Buttons */
    .btn {
      padding: 12px 24px;
      border: none;
      border-radius: var(--radius-sm);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .btn-primary {
      background: var(--primary);
      color: white;
    }

    .btn-primary:hover {
      background: var(--primary-hover);
      transform: translateY(-1px);
    }

    .btn-secondary {
      background: var(--secondary);
      color: var(--text);
    }

    .btn-secondary:hover {
      background: #e5e7eb;
    }

    .btn-danger {
      background: var(--danger);
      color: white;
    }

    .btn-danger:hover {
      opacity: 0.9;
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    /* ===== TEACH Panel ===== */
    .question-card {
      padding: 32px 24px;
      text-align: center;
    }

    .question-progress {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: var(--secondary);
      border-radius: 20px;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 24px;
    }

    .question-progress .current {
      font-weight: 700;
      color: var(--primary);
    }

    .question-text {
      font-size: 20px;
      font-weight: 600;
      line-height: 1.5;
      margin-bottom: 32px;
      min-height: 90px;
    }

    .choices {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .choice-btn {
      width: 100%;
      padding: 18px 24px;
      background: var(--secondary);
      border: 2px solid transparent;
      border-radius: var(--radius-sm);
      font-size: 15px;
      font-weight: 500;
      color: var(--text);
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: left;
    }

    .choice-btn:hover {
      border-color: var(--primary);
      background: #eef2ff;
    }

    .choice-btn:active {
      transform: scale(0.98);
    }

    .choice-btn .label {
      display: inline-block;
      width: 28px;
      height: 28px;
      line-height: 28px;
      text-align: center;
      background: var(--primary);
      color: white;
      border-radius: 8px;
      font-weight: 700;
      font-size: 13px;
      margin-right: 12px;
    }

    /* Reaction */
    .reaction-box {
      padding: 20px 24px;
      background: linear-gradient(135deg, #f0fdf4, #ecfeff);
      border-top: 1px solid var(--border);
      text-align: center;
      display: none;
    }

    .reaction-box.show {
      display: block;
    }

    .reaction-box .emoji {
      font-size: 32px;
      margin-bottom: 8px;
    }

    .reaction-box .text {
      font-size: 15px;
      color: var(--text);
    }

    /* Timeout warning */
    .timeout-bar {
      height: 4px;
      background: var(--secondary);
      margin-top: 16px;
      border-radius: 2px;
      overflow: hidden;
    }

    .timeout-bar .progress {
      height: 100%;
      background: linear-gradient(90deg, var(--accent), var(--primary));
      width: 100%;
      transition: width 0.1s linear;
    }

    /* ===== TALK Panel ===== */
    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 400px;
    }

    .topic-selector {
      padding: 16px;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .topic-selector select {
      flex: 1;
      padding: 10px 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 14px;
      background: var(--card);
      outline: none;
    }

    .chat-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #f9fafb;
    }

    .message {
      max-width: 85%;
      padding: 12px 16px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.5;
      animation: fadeIn 0.2s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .message.user {
      align-self: flex-end;
      background: var(--primary);
      color: white;
      border-bottom-right-radius: 6px;
    }

    .message.assistant {
      align-self: flex-start;
      background: var(--card);
      border: 1px solid var(--border);
      border-bottom-left-radius: 6px;
    }

    .message.system {
      align-self: center;
      background: transparent;
      color: var(--muted);
      font-size: 12px;
      padding: 8px 16px;
    }

    .message.typing {
      background: var(--card);
      border: 1px solid var(--border);
    }

    .typing-dots {
      display: flex;
      gap: 4px;
    }

    .typing-dots span {
      width: 8px;
      height: 8px;
      background: var(--muted);
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;
    }

    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }

    .chat-input {
      padding: 16px;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 12px;
      background: var(--card);
    }

    .chat-input textarea {
      flex: 1;
      padding: 12px 16px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 14px;
      resize: none;
      outline: none;
      font-family: inherit;
      min-height: 44px;
      max-height: 120px;
    }

    .chat-input textarea:focus {
      border-color: var(--primary);
    }

    .chat-input .btn {
      align-self: flex-end;
    }

    /* Status */
    .status {
      text-align: center;
      padding: 12px;
      font-size: 12px;
      color: var(--muted);
    }

    .status.error {
      color: var(--danger);
      background: #fef2f2;
    }

    /* Loading */
    .loading {
      display: none;
      justify-content: center;
      padding: 40px;
    }

    .loading.show {
      display: flex;
    }

    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid var(--secondary);
      border-top-color: var(--primary);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Empty state */
    .empty-state {
      text-align: center;
      padding: 60px 24px;
      color: var(--muted);
    }

    .empty-state .icon {
      font-size: 48px;
      margin-bottom: 16px;
    }

    .empty-state h3 {
      color: var(--text);
      margin-bottom: 8px;
    }
  </style>
</head>

<body>
  <div class="container">
    <header class="header">
      <h1>Psano</h1>
      <p>페르소나 테스트</p>
    </header>

    <!-- Session Bar -->
    <div class="session-bar">
      <input type="text" id="visitorName" placeholder="이름을 입력하세요" />
      <button class="btn btn-primary" id="sessionBtn" onclick="toggleSession()">시작</button>
    </div>
    <div class="session-info" id="sessionInfo">
      세션을 시작하려면 이름을 입력하고 시작 버튼을 누르세요
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab active" data-panel="teach" onclick="switchTab('teach')">
        형성기
      </button>
      <button class="tab" data-panel="talk" onclick="switchTab('talk')">
        대화기
      </button>
    </div>

    <!-- TEACH Panel -->
    <div class="panel active" id="teachPanel">
      <div class="card">
        <div class="question-card" id="questionCard">
          <div class="empty-state" id="teachEmpty">
            <div class="icon">📝</div>
            <h3>질문 대기 중</h3>
            <p>세션을 시작하면 질문이 표시됩니다</p>
          </div>

          <div id="questionContent" style="display:none">
            <div class="question-progress">
              <span class="current" id="qIndex">1</span>
              <span>/ 5</span>
            </div>
            <div class="question-text" id="questionText">질문이 여기에 표시됩니다</div>
            <div class="choices">
              <button class="choice-btn" onclick="answer('A')">
                <span class="label">A</span>
                <span id="choiceA">선택지 A</span>
              </button>
              <button class="choice-btn" onclick="answer('B')">
                <span class="label">B</span>
                <span id="choiceB">선택지 B</span>
              </button>
            </div>
          </div>

          <div class="loading" id="teachLoading">
            <div class="spinner"></div>
          </div>
        </div>

        <div class="reaction-box" id="reactionBox">
          <div class="text" id="reactionText"></div>
        </div>

        <div class="timeout-bar" id="timeoutBar" style="display:none">
          <div class="progress" id="timeoutProgress"></div>
        </div>
      </div>

      <div class="status" id="teachStatus"></div>
    </div>

    <!-- TALK Panel -->
    <div class="panel" id="talkPanel">
      <div class="card chat-container">
        <div class="topic-selector">
          <select id="topicSelect">
            <option value="1">주제 1</option>
            <option value="2">주제 2</option>
            <option value="3">주제 3</option>
          </select>
          <button class="btn btn-secondary" onclick="startTalk()">대화 시작</button>
        </div>

        <div class="chat-messages" id="chatMessages">
          <div class="empty-state" id="talkEmpty">
            <div class="icon">💬</div>
            <h3>대화를 시작해보세요</h3>
            <p>주제를 선택하고 대화 시작 버튼을 누르세요</p>
          </div>
        </div>

        <div class="chat-input">
          <textarea id="chatInput" placeholder="메시지를 입력하세요..." rows="1" disabled></textarea>
          <button class="btn btn-primary" onclick="sendMessage()" id="sendBtn" disabled>전송</button>
        </div>
      </div>

      <div class="status" id="talkStatus"></div>
    </div>
  </div>

<script>
  // State
  let sessionId = null;
  let currentQuestionId = null;
  let topicId = null;
  let talkStarted = false;

  // Timeout timer (5분)
  let timeoutTimer = null;
  let timeoutStartTime = null;
  const TIMEOUT_MS = 5 * 60 * 1000;

  // Elements
  const sessionBtn = document.getElementById('sessionBtn');
  const sessionInfo = document.getElementById('sessionInfo');
  const visitorNameInput = document.getElementById('visitorName');

  // Teach elements
  const teachEmpty = document.getElementById('teachEmpty');
  const questionContent = document.getElementById('questionContent');
  const questionText = document.getElementById('questionText');
  const choiceA = document.getElementById('choiceA');
  const choiceB = document.getElementById('choiceB');
  const qIndex = document.getElementById('qIndex');
  const reactionBox = document.getElementById('reactionBox');
  const reactionText = document.getElementById('reactionText');
  const teachLoading = document.getElementById('teachLoading');
  const teachStatus = document.getElementById('teachStatus');
  const timeoutBar = document.getElementById('timeoutBar');
  const timeoutProgress = document.getElementById('timeoutProgress');

  // Talk elements
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const topicSelect = document.getElementById('topicSelect');
  const talkEmpty = document.getElementById('talkEmpty');
  const talkStatus = document.getElementById('talkStatus');

  // Utils
  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || res.statusText);
    return data;
  }

  function showLoading(el, show) {
    el.classList.toggle('show', show);
  }

  // Tab switching
  function switchTab(panel) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelector(`[data-panel="${panel}"]`).classList.add('active');
    document.getElementById(`${panel}Panel`).classList.add('active');
  }

  // Session management
  async function toggleSession() {
    if (sessionId) {
      await endSession();
    } else {
      await startSession();
    }
  }

  async function startSession() {
    const name = visitorNameInput.value.trim();
    if (!name) {
      teachStatus.textContent = '이름을 입력해주세요';
      teachStatus.classList.add('error');
      return;
    }

    try {
      const data = await fetchJson('/session/start', {
        method: 'POST',
        body: JSON.stringify({ visitor_name: name })
      });

      sessionId = data.session_id;
      sessionBtn.textContent = '종료';
      sessionBtn.classList.remove('btn-primary');
      sessionBtn.classList.add('btn-danger');
      visitorNameInput.disabled = true;
      sessionInfo.innerHTML = `세션 ID: <strong>${sessionId}</strong> | Phase: ${data.phase}`;
      teachStatus.textContent = '';
      teachStatus.classList.remove('error');

      // Load first question
      await loadQuestion();
      startTimeoutTimer();

    } catch (e) {
      teachStatus.textContent = `오류: ${e.message}`;
      teachStatus.classList.add('error');
    }
  }

  async function endSession(reason = 'completed') {
    if (!sessionId) return;

    clearTimeoutTimer();

    try {
      await fetchJson('/session/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, reason })
      });
    } catch (e) {
      console.error('End session error:', e);
    }

    // Reset state
    sessionId = null;
    currentQuestionId = null;
    talkStarted = false;
    topicId = null;

    sessionBtn.textContent = '시작';
    sessionBtn.classList.remove('btn-danger');
    sessionBtn.classList.add('btn-primary');
    visitorNameInput.disabled = false;
    sessionInfo.textContent = '세션을 시작하려면 이름을 입력하고 시작 버튼을 누르세요';

    // Reset teach panel
    teachEmpty.style.display = 'block';
    questionContent.style.display = 'none';
    reactionBox.classList.remove('show');
    timeoutBar.style.display = 'none';

    // Reset talk panel
    chatMessages.innerHTML = '';
    talkEmpty.style.display = 'block';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    teachStatus.textContent = reason === 'timeout' ? '시간 초과로 세션이 종료되었습니다' : '';
  }

  // Timeout timer
  function startTimeoutTimer() {
    clearTimeoutTimer();
    timeoutStartTime = Date.now();
    timeoutBar.style.display = 'block';

    function updateProgress() {
      const elapsed = Date.now() - timeoutStartTime;
      const remaining = Math.max(0, TIMEOUT_MS - elapsed);
      const percent = (remaining / TIMEOUT_MS) * 100;
      timeoutProgress.style.width = percent + '%';

      if (remaining <= 0) {
        endSession('timeout');
      } else {
        timeoutTimer = requestAnimationFrame(updateProgress);
      }
    }
    updateProgress();
  }

  function clearTimeoutTimer() {
    if (timeoutTimer) {
      cancelAnimationFrame(timeoutTimer);
      timeoutTimer = null;
    }
    timeoutBar.style.display = 'none';
  }

  function resetTimeoutTimer() {
    if (sessionId) {
      startTimeoutTimer();
    }
  }

  // TEACH: Load question
  async function loadQuestion() {
    if (!sessionId) return;

    showLoading(teachLoading, true);
    teachEmpty.style.display = 'none';
    questionContent.style.display = 'none';
    reactionBox.classList.remove('show');

    try {
      const data = await fetchJson(`/question/current?session_id=${sessionId}`);

      currentQuestionId = data.id;
      qIndex.textContent = data.session_question_index || '?';
      questionText.textContent = data.question_text;
      choiceA.textContent = data.choice_a;
      choiceB.textContent = data.choice_b;

      questionContent.style.display = 'block';
      teachStatus.textContent = '';
      teachStatus.classList.remove('error');

    } catch (e) {
      teachStatus.textContent = `오류: ${e.message}`;
      teachStatus.classList.add('error');
      teachEmpty.style.display = 'block';
    } finally {
      showLoading(teachLoading, false);
    }
  }

  // TEACH: Answer
  async function answer(choice) {
    if (!sessionId || !currentQuestionId) return;

    showLoading(teachLoading, true);
    questionContent.style.display = 'none';

    try {
      const data = await fetchJson('/answer', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          question_id: currentQuestionId,
          choice
        })
      });

      // Show reaction
      reactionText.textContent = data.assistant_reaction_text || '다음으로 넘어갈게요';
      reactionBox.classList.add('show');

      resetTimeoutTimer();

      // Check if session should end
      if (data.session_should_end) {
        teachStatus.textContent = '형성기 질문이 완료되었습니다! 세션을 종료하세요.';
        clearTimeoutTimer();

        setTimeout(() => {
          endSession('completed');
        }, 2000);
      } else {
        // Load next question after delay
        setTimeout(async () => {
          reactionBox.classList.remove('show');
          await loadQuestion();
        }, 1500);
      }

    } catch (e) {
      teachStatus.textContent = `오류: ${e.message}`;
      teachStatus.classList.add('error');
      questionContent.style.display = 'block';
    } finally {
      showLoading(teachLoading, false);
    }
  }

  // TALK: Load topics
  async function loadTopics() {
    try {
      const data = await fetchJson('/talk/topics');
      const topics = data.topics || [];

      topicSelect.innerHTML = '';
      topics.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = `${t.id}. ${t.title}`;
        topicSelect.appendChild(opt);
      });
    } catch (e) {
      console.error('Load topics error:', e);
    }
  }

  // TALK: Start
  async function startTalk() {
    if (!sessionId) {
      talkStatus.textContent = '먼저 세션을 시작해주세요';
      talkStatus.classList.add('error');
      return;
    }

    topicId = parseInt(topicSelect.value);

    try {
      const data = await fetchJson('/talk/start', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          topic_id: topicId
        })
      });

      talkStarted = true;
      talkEmpty.style.display = 'none';
      chatInput.disabled = false;
      sendBtn.disabled = false;
      talkStatus.textContent = '';
      talkStatus.classList.remove('error');

      // Show first message
      const firstMsg = data.assistant_first_text || data.ui_text || '';
      if (firstMsg) {
        addMessage('assistant', firstMsg);
      }

    } catch (e) {
      talkStatus.textContent = `오류: ${e.message}`;
      talkStatus.classList.add('error');
    }
  }

  // TALK: Send message
  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text || !sessionId || !talkStarted) return;

    addMessage('user', text);
    chatInput.value = '';

    // Show typing indicator
    const typingEl = addMessage('assistant typing', '');
    typingEl.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';

    try {
      const data = await fetchJson('/talk/turn', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          topic_id: topicId,
          user_text: text
        })
      });

      // Replace typing with response
      const response = data.ui_text || data.assistant_text || '';
      typingEl.classList.remove('typing');
      typingEl.textContent = response;

    } catch (e) {
      typingEl.remove();
      talkStatus.textContent = `오류: ${e.message}`;
      talkStatus.classList.add('error');
    }
  }

  function addMessage(type, text) {
    const msg = document.createElement('div');
    msg.className = `message ${type}`;
    msg.textContent = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
  }

  // Chat input events
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Auto-resize textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });

  // Init
  loadTopics();
</script>

</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
def test_ui():
    return HTMLResponse(content=HTML)