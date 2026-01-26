from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = r"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Psano Console</title>
  <style>
    :root {
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #1e293b;
      --muted: #64748b;
      --border: #e2e8f0;
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --secondary: #f1f5f9;
      --accent: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
      --radius: 12px;
      --radius-sm: 8px;
      --mono: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
    }

    /* Layout */
    .app {
      display: flex;
      min-height: 100vh;
    }

    .sidebar {
      width: 280px;
      background: var(--card);
      border-right: 1px solid var(--border);
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      position: fixed;
      height: 100vh;
      overflow-y: auto;
    }

    .main {
      flex: 1;
      margin-left: 280px;
      padding: 24px;
      max-width: 900px;
    }

    /* Logo */
    .logo {
      font-size: 24px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }

    /* Status pill */
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: var(--secondary);
      border-radius: 20px;
      font-size: 12px;
      font-family: var(--mono);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--warning);
    }

    .status-dot.ok { background: var(--accent); }
    .status-dot.error { background: var(--danger); }

    /* Session card */
    .session-card {
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      border-radius: var(--radius);
      padding: 16px;
      color: white;
    }

    .session-card .label {
      font-size: 11px;
      opacity: 0.8;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .session-card .value {
      font-size: 18px;
      font-weight: 600;
      font-family: var(--mono);
    }

    .session-card input {
      width: 100%;
      padding: 10px 12px;
      border: none;
      border-radius: var(--radius-sm);
      background: rgba(255,255,255,0.2);
      color: white;
      font-size: 14px;
      margin-top: 8px;
    }

    .session-card input::placeholder { color: rgba(255,255,255,0.6); }
    .session-card input:focus { outline: none; background: rgba(255,255,255,0.3); }

    .session-btns {
      display: flex;
      gap: 8px;
      margin-top: 12px;
    }

    .session-btns .btn {
      flex: 1;
      padding: 10px;
      font-size: 13px;
    }

    /* Nav */
    .nav {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      font-size: 14px;
      color: var(--muted);
      cursor: pointer;
      transition: all 0.15s;
      border: none;
      background: none;
      width: 100%;
      text-align: left;
    }

    .nav-item:hover { background: var(--secondary); color: var(--text); }
    .nav-item.active { background: var(--primary); color: white; }
    .nav-item .icon { font-size: 18px; }

    /* Cards */
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      margin-bottom: 20px;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
    }

    .card-title {
      font-size: 15px;
      font-weight: 600;
    }

    .card-body { padding: 20px; }

    /* Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 8px 16px;
      border: none;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
    }

    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-secondary { background: var(--secondary); color: var(--text); }
    .btn-secondary:hover { background: #e2e8f0; }
    .btn-danger { background: var(--danger); color: white; }
    .btn-danger:hover { opacity: 0.9; }
    .btn-ghost { background: transparent; color: var(--muted); }
    .btn-ghost:hover { background: var(--secondary); color: var(--text); }
    .btn-sm { padding: 6px 12px; font-size: 12px; }

    /* Form elements */
    input, textarea, select {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 14px;
      background: var(--card);
      color: var(--text);
      transition: border-color 0.15s;
    }

    input:focus, textarea:focus, select:focus {
      outline: none;
      border-color: var(--primary);
    }

    textarea { min-height: 80px; resize: vertical; font-family: inherit; }

    .form-group { margin-bottom: 16px; }
    .form-label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: var(--muted);
      margin-bottom: 6px;
    }

    .form-row {
      display: flex;
      gap: 12px;
      align-items: flex-end;
    }

    .form-row > * { flex: 1; }

    /* Badges */
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      background: var(--secondary);
      border-radius: 6px;
      font-size: 12px;
      font-family: var(--mono);
      color: var(--muted);
    }

    .badge-primary { background: #eef2ff; color: var(--primary); }
    .badge-success { background: #ecfdf5; color: var(--accent); }

    /* Output box */
    .output {
      background: #1e293b;
      color: #e2e8f0;
      border-radius: var(--radius-sm);
      padding: 16px;
      font-family: var(--mono);
      font-size: 12px;
      line-height: 1.6;
      max-height: 300px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }

    /* Question box */
    .question-box {
      background: var(--secondary);
      border-radius: var(--radius-sm);
      padding: 20px;
      text-align: center;
    }

    .question-text {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 20px;
      line-height: 1.6;
    }

    .choices {
      display: flex;
      gap: 12px;
    }

    .choice-btn {
      flex: 1;
      padding: 16px 20px;
      background: var(--card);
      border: 2px solid var(--border);
      border-radius: var(--radius-sm);
      font-size: 14px;
      cursor: pointer;
      transition: all 0.15s;
    }

    .choice-btn:hover {
      border-color: var(--primary);
      background: #eef2ff;
    }

    .choice-btn .label {
      display: block;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 4px;
    }

    /* Chat */
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 500px;
    }

    .chat-header {
      display: flex;
      gap: 12px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 16px;
    }

    .chat-messages {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 4px;
    }

    .message {
      max-width: 80%;
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.5;
    }

    .message.user {
      align-self: flex-end;
      background: var(--primary);
      color: white;
      border-bottom-right-radius: 4px;
    }

    .message.assistant {
      align-self: flex-start;
      background: var(--secondary);
      border-bottom-left-radius: 4px;
    }

    .message.system {
      align-self: center;
      background: transparent;
      color: var(--muted);
      font-size: 12px;
    }

    .chat-input-bar {
      display: flex;
      gap: 12px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
      margin-top: 16px;
    }

    .chat-input-bar textarea {
      flex: 1;
      min-height: 44px;
      max-height: 120px;
      resize: none;
    }

    /* Table */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    th, td {
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }

    th {
      font-weight: 600;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Grid */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
    .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }

    /* Section */
    .section {
      display: none;
    }

    .section.active {
      display: block;
    }

    /* Divider */
    .divider {
      height: 1px;
      background: var(--border);
      margin: 20px 0;
    }

    /* Checkbox */
    .checkbox-group {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
    }

    .checkbox {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      cursor: pointer;
    }

    .checkbox input { width: auto; }

    /* Variable tag button */
    .var-tag {
      display: inline-block;
      padding: 4px 8px;
      background: var(--secondary);
      border: 1px solid var(--border);
      border-radius: 4px;
      font-family: var(--mono);
      font-size: 11px;
      color: var(--primary);
      cursor: pointer;
      transition: all 0.15s;
    }

    .var-tag:hover {
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }

    /* File input */
    input[type="file"] {
      padding: 8px;
      font-size: 13px;
    }

    /* Spinner */
    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid var(--border);
      border-top-color: var(--primary);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      display: none;
    }

    .spinner.show { display: inline-block; }

    @keyframes spin { to { transform: rotate(360deg); } }

    /* Stats */
    .stats {
      display: flex;
      gap: 16px;
    }

    .stat {
      flex: 1;
      background: var(--secondary);
      border-radius: var(--radius-sm);
      padding: 16px;
      text-align: center;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: var(--primary);
      font-family: var(--mono);
    }

    .stat-label {
      font-size: 11px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 4px;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar { display: none; }
      .main { margin-left: 0; }
    }

    /* Toast */
    .toast-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .toast {
      padding: 14px 20px;
      border-radius: var(--radius-sm);
      box-shadow: var(--shadow-lg);
      font-size: 13px;
      animation: slideIn 0.3s ease;
      max-width: 360px;
    }

    .toast.error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #dc2626;
    }

    .toast.success {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #16a34a;
    }

    .toast.info {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      color: #2563eb;
    }

    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }

    /* Help Modal */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 10000;
    }

    .modal-overlay.show {
      display: flex;
    }

    .modal {
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      max-width: 600px;
      width: 90%;
      max-height: 80vh;
      overflow: hidden;
      animation: modalIn 0.2s ease;
    }

    @keyframes modalIn {
      from { transform: scale(0.95); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }

    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
    }

    .modal-title {
      font-size: 16px;
      font-weight: 600;
    }

    .modal-close {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: var(--muted);
      padding: 4px 8px;
      border-radius: 4px;
    }

    .modal-close:hover {
      background: var(--secondary);
      color: var(--text);
    }

    .modal-body {
      padding: 20px;
      overflow-y: auto;
      max-height: calc(80vh - 60px);
    }

    .help-section {
      margin-bottom: 20px;
    }

    .help-section:last-child {
      margin-bottom: 0;
    }

    .help-section h4 {
      font-size: 14px;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .help-section p {
      font-size: 13px;
      color: var(--text);
      line-height: 1.6;
      margin-bottom: 8px;
    }

    .help-section ul {
      font-size: 13px;
      color: var(--muted);
      margin-left: 20px;
      line-height: 1.8;
    }

    .help-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--secondary);
      border: 1px solid var(--border);
      color: var(--muted);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .help-btn:hover {
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }
  </style>
</head>

<body>
  <div class="toast-container" id="toastContainer"></div>

  <!-- Help Modal -->
  <div class="modal-overlay" id="helpModal" onclick="closeHelpModal(event)">
    <div class="modal" onclick="event.stopPropagation()">
      <div class="modal-header">
        <span class="modal-title">Psano Console 도움말</span>
        <button class="modal-close" onclick="closeHelpModal()">&times;</button>
      </div>
      <div class="modal-body" id="helpModalBody">
        <!-- Content will be dynamically loaded -->
      </div>
    </div>
  </div>

  <div class="app">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <div class="logo">Psano</div>
          <button class="help-btn" onclick="showHelp()" title="도움말">?</button>
        </div>
        <div class="status-pill">
          <span class="status-dot" id="statusDot"></span>
          <span id="statusText">connecting...</span>
          <div class="spinner" id="spinner"></div>
        </div>
      </div>

      <!-- Session -->
      <div class="session-card">
        <div class="label">Session</div>
        <div class="value" id="sessionId">-</div>
        <input type="text" id="visitorName" placeholder="방문자 이름 입력..." />
        <div class="session-btns">
          <button class="btn btn-secondary" onclick="startSession()">Start</button>
          <button class="btn btn-danger" onclick="endSession()">End</button>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="nav">
        <button class="nav-item active" onclick="showSection('formation')">
          <span class="icon">📝</span> Formation
        </button>
        <button class="nav-item" onclick="showSection('talk')">
          <span class="icon">💬</span> Talk
        </button>
        <button class="nav-item" onclick="showSection('admin')">
          <span class="icon">⚙️</span> Admin
        </button>
        <button class="nav-item" onclick="showSection('debug')">
          <span class="icon">🔍</span> Debug
        </button>
      </nav>

      <!-- Quick stats -->
      <div style="margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border);">
        <div class="form-label">Current State</div>
        <div style="display: flex; flex-direction: column; gap: 6px; font-size: 12px; font-family: var(--mono);">
          <div>Phase: <strong id="statePhase">-</strong></div>
          <div>Question: <strong id="stateQuestion">-</strong></div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main">
      <!-- Formation Section -->
      <section class="section active" id="sectionFormation">
        <!-- Idle & Monologue Test -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Idle State (클릭 시 인사/혼잣말)</span>
            <div style="display: flex; gap: 8px; align-items: center;">
              <span class="badge badge-primary" id="stageBadge">stage: -</span>
            </div>
          </div>
          <div class="card-body">
            <div class="grid-2" style="margin-bottom: 16px;">
              <button class="btn btn-primary" onclick="testIdleGreeting()">Idle Greeting (인사말)</button>
              <button class="btn btn-secondary" onclick="testIdleMonologue()">Idle Monologue (혼잣말)</button>
            </div>
            <div id="idleResultBox" style="padding: 20px; background: var(--secondary); border-radius: 8px; display: none;">
              <div style="font-size: 12px; color: var(--muted); margin-bottom: 8px;">
                <span id="idleStageInfo">-</span>
              </div>
              <div id="idleResultText" style="font-size: 15px; line-height: 1.8; white-space: pre-wrap;"></div>
            </div>
          </div>
        </div>

        <!-- Question Card -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Formation (A/B 질문)</span>
            <div style="display: flex; gap: 8px; align-items: center;">
              <span class="badge" id="qBadge">question: -</span>
              <button class="btn btn-sm btn-secondary" onclick="getCurrentQuestion()">Load Question</button>
            </div>
          </div>
          <div class="card-body">
            <div class="question-box" id="questionBox">
              <div class="question-text" id="questionText">질문을 불러오세요</div>
              <div class="choices">
                <button class="choice-btn" onclick="sendAnswer('A')">
                  <span class="label">A</span>
                  <span id="choiceA">-</span>
                </button>
                <button class="choice-btn" onclick="sendAnswer('B')">
                  <span class="label">B</span>
                  <span id="choiceB">-</span>
                </button>
              </div>
            </div>
            <div id="reactionBox" style="margin-top: 16px; padding: 16px; background: #ecfdf5; border-radius: 8px; display: none;">
              <strong>사노:</strong> <span id="reactionText"></span>
            </div>
          </div>
        </div>
      </section>

      <!-- Talk Section -->
      <section class="section" id="sectionTalk">
        <div class="card">
          <div class="card-header">
            <span class="card-title">Talk (대화)</span>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-ghost" onclick="loadTopics()">Load Topics</button>
              <button class="btn btn-sm btn-secondary" onclick="talkNudge()">Nudge (재촉)</button>
              <button class="btn btn-sm btn-danger" onclick="talkEnd()">End Talk</button>
            </div>
          </div>
          <div class="card-body">
            <div class="chat-container">
              <div class="chat-header">
                <select id="topicSelect" style="flex: 1;">
                  <option value="1">Topic 1</option>
                </select>
                <button class="btn btn-primary" onclick="talkStart()">Start Talk</button>
              </div>
              <div class="chat-messages" id="chatMessages">
                <div class="message system">대화를 시작하려면 주제를 선택하고 Start Talk을 누르세요</div>
              </div>
              <div class="chat-input-bar">
                <textarea id="talkInput" placeholder="메시지 입력... (Enter: 전송)" disabled></textarea>
                <button class="btn btn-primary" onclick="sendTalk()" id="sendTalkBtn" disabled>Send</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Admin Section -->
      <section class="section" id="sectionAdmin">
        <!-- Progress -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Progress</span>
            <button class="btn btn-sm btn-secondary" onclick="fetchAdminProgress()">Refresh</button>
          </div>
          <div class="card-body">
            <div class="stats">
              <div class="stat">
                <div class="stat-value" id="admAnswered">-</div>
                <div class="stat-label">Answered</div>
              </div>
              <div class="stat">
                <div class="stat-value" id="admMax">380</div>
                <div class="stat-label">Total</div>
              </div>
              <div class="stat">
                <div class="stat-value" id="admRatio">-</div>
                <div class="stat-label">Progress</div>
              </div>
              <div class="stat">
                <div class="stat-value" id="admPhase">-</div>
                <div class="stat-label">Phase</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Reset -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Reset</span>
          </div>
          <div class="card-body">
            <div class="checkbox-group" style="margin-bottom: 16px;">
              <label class="checkbox"><input type="checkbox" id="resetAnswers" /> answers</label>
              <label class="checkbox"><input type="checkbox" id="resetSessions" /> sessions</label>
              <label class="checkbox"><input type="checkbox" id="resetState" /> state</label>
              <label class="checkbox"><input type="checkbox" id="resetPersonality" /> personality</label>
            </div>
            <button class="btn btn-danger" onclick="adminReset()">Reset Selected</button>
          </div>
        </div>

        <!-- Phase & Question -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">State Control</span>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Phase</label>
                <div class="form-row">
                  <select id="admPhaseSelect">
                    <option value="teach">teach</option>
                    <option value="talk">talk</option>
                  </select>
                  <button class="btn btn-secondary" onclick="adminSetPhase()">Apply</button>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Current Question</label>
                <div class="form-row">
                  <input type="number" id="admSetQ" value="1" />
                  <button class="btn btn-secondary" onclick="adminSetCurrentQuestion()">Apply</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Import -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Import</span>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Questions (xlsx)</label>
                <input type="file" id="admXlsxFile" accept=".xlsx" />
                <button class="btn btn-primary btn-sm" style="margin-top: 8px;" onclick="adminImportQuestions()">Upload</button>
              </div>
              <div class="form-group">
                <label class="form-label">Settings (xlsx)</label>
                <input type="file" id="admSettingsXlsxFile" accept=".xlsx" />
                <button class="btn btn-primary btn-sm" style="margin-top: 8px;" onclick="adminImportSettings()">Upload</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Persona -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Persona Generate</span>
          </div>
          <div class="card-body">
            <div class="form-row">
              <div class="form-group" style="flex: 2;">
                <label class="form-label">Model</label>
                <select id="personaModel">
                  <option value="gpt-4o-mini">gpt-4o-mini (Fast, Cheap)</option>
                  <option value="gpt-4o">gpt-4o (Balanced)</option>
                  <option value="gpt-4-turbo">gpt-4-turbo (High Quality)</option>
                  <option value="gpt-3.5-turbo">gpt-3.5-turbo (Legacy)</option>
                  <option value="o1-mini">o1-mini (Reasoning)</option>
                  <option value="o1-preview">o1-preview (Advanced Reasoning)</option>
                </select>
              </div>
              <div class="form-group" style="flex: 1;">
                <label class="form-label">Max Tokens</label>
                <input type="number" id="personaMaxTokens" placeholder="1200" />
              </div>
              <div class="form-group" style="flex: 0;">
                <label class="form-label">&nbsp;</label>
                <label class="checkbox"><input type="checkbox" id="personaForce" /> force</label>
              </div>
              <div class="form-group" style="flex: 0;">
                <label class="form-label">&nbsp;</label>
                <button class="btn btn-primary" onclick="personaGenerate()">Generate</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Personality -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Personality Values</span>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-secondary" onclick="fetchAdminPersonality()">Load</button>
              <button class="btn btn-sm btn-primary" onclick="adminSetPersonality()">Apply</button>
            </div>
          </div>
          <div class="card-body">
            <div class="grid-5">
              <div class="form-group">
                <label class="form-label">self_direction</label>
                <input type="number" id="pSelfDirection" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">conformity</label>
                <input type="number" id="pConformity" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">stimulation</label>
                <input type="number" id="pStimulation" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">security</label>
                <input type="number" id="pSecurity" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">hedonism</label>
                <input type="number" id="pHedonism" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">tradition</label>
                <input type="number" id="pTradition" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">achievement</label>
                <input type="number" id="pAchievement" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">benevolence</label>
                <input type="number" id="pBenevolence" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">power</label>
                <input type="number" id="pPower" value="0" />
              </div>
              <div class="form-group">
                <label class="form-label">universalism</label>
                <input type="number" id="pUniversalism" value="0" />
              </div>
            </div>
          </div>
        </div>

        <!-- Sessions -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Recent Sessions</span>
            <div style="display: flex; gap: 8px; align-items: center;">
              <input type="number" id="admLimit" value="20" style="width: 60px;" />
              <input type="number" id="admOffset" value="0" style="width: 60px;" />
              <button class="btn btn-sm btn-secondary" onclick="fetchAdminSessions()">Load</button>
            </div>
          </div>
          <div class="card-body">
            <div id="admSessionsBox" style="overflow-x: auto;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch sessions</div>
            </div>
          </div>
        </div>

        <!-- Config Management -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Config Settings</span>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-secondary" onclick="loadConfigs()">Load</button>
              <button class="btn btn-sm btn-ghost" onclick="clearConfigCache()">Clear Cache</button>
            </div>
          </div>
          <div class="card-body">
            <div id="configTableBox" style="overflow-x: auto; max-height: 400px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch configs</div>
            </div>
          </div>
        </div>

        <!-- Prompts Management -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Prompt Templates</span>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-secondary" onclick="loadPrompts()">Load</button>
              <button class="btn btn-sm btn-ghost" onclick="clearPromptCache()">Clear Cache</button>
            </div>
          </div>
          <div class="card-body">
            <div class="form-group" style="margin-bottom: 12px;">
              <label class="form-label">Select Prompt</label>
              <select id="promptSelect" onchange="onPromptSelect()" style="width: 100%;">
                <option value="">-- Load prompts first --</option>
              </select>
            </div>
            <div id="promptVarsBox" style="margin-bottom: 12px; display: none;">
              <label class="form-label">Available Variables <span style="color: var(--muted); font-size: 11px;">(click to insert)</span></label>
              <div id="promptVarButtons" style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px;"></div>
            </div>
            <div class="form-group" style="margin-bottom: 12px;">
              <label class="form-label">Template</label>
              <textarea id="promptTemplate" rows="14" style="font-family: var(--mono); font-size: 12px; width: 100%;"></textarea>
            </div>
            <div style="display: flex; gap: 8px; justify-content: flex-end;">
              <button class="btn btn-primary" onclick="savePrompt()">Save Prompt</button>
            </div>
          </div>
        </div>

        <!-- Quick Test -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Quick Test</span>
          </div>
          <div class="card-body">
            <p style="font-size: 13px; color: var(--muted); margin-bottom: 12px;">세션 생성 → 랜덤 답변 제출 → 세션 종료를 자동으로 실행합니다.</p>
            <div class="form-row">
              <div class="form-group" style="flex: 2;">
                <label class="form-label">방문자 이름</label>
                <input type="text" id="quickTestName" value="QuickTest" />
              </div>
              <div class="form-group" style="flex: 1;">
                <label class="form-label">답변 수</label>
                <input type="number" id="quickTestCount" value="5" min="1" max="10" />
              </div>
              <div class="form-group" style="flex: 0;">
                <label class="form-label">&nbsp;</label>
                <button class="btn btn-primary" onclick="runQuickTest()">Run Test</button>
              </div>
            </div>
            <div id="quickTestResult" style="display: none; margin-top: 12px; padding: 12px; background: var(--secondary); border-radius: 8px; font-size: 12px; font-family: var(--mono);"></div>
          </div>
        </div>

        <!-- Current Persona -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Current Persona</span>
            <button class="btn btn-sm btn-secondary" onclick="loadCurrentPersona()">Load</button>
          </div>
          <div class="card-body">
            <div id="personaInfoBox" style="margin-bottom: 12px; font-size: 13px; color: var(--muted);">Click Load to view current persona</div>
            <div id="personaPromptBox" style="display: none;">
              <div class="form-label">Values Summary</div>
              <div id="personaValuesSummary" style="padding: 12px; background: var(--secondary); border-radius: 8px; font-size: 12px; margin-bottom: 12px; white-space: pre-wrap; max-height: 150px; overflow-y: auto;"></div>
              <div class="form-label">Persona Prompt</div>
              <div id="personaPromptText" style="padding: 12px; background: #1e293b; color: #e2e8f0; border-radius: 8px; font-size: 12px; font-family: var(--mono); white-space: pre-wrap; max-height: 300px; overflow-y: auto;"></div>
            </div>
          </div>
        </div>

        <!-- Questions List -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Questions</span>
            <div style="display: flex; gap: 8px; align-items: center;">
              <label class="checkbox" style="font-size: 12px;"><input type="checkbox" id="questionsEnabledOnly" /> enabled only</label>
              <input type="number" id="questionsLimit" value="20" style="width: 50px;" placeholder="limit" />
              <input type="number" id="questionsOffset" value="0" style="width: 50px;" placeholder="offset" />
              <button class="btn btn-sm btn-secondary" onclick="loadQuestions()">Load</button>
            </div>
          </div>
          <div class="card-body">
            <div id="questionsBox" style="overflow-x: auto; max-height: 400px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch questions</div>
            </div>
          </div>
        </div>

        <!-- Growth Stages -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Growth Stages</span>
            <button class="btn btn-sm btn-secondary" onclick="loadGrowthStages()">Load</button>
          </div>
          <div class="card-body">
            <div id="growthStagesBox" style="overflow-x: auto;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch growth stages</div>
            </div>
          </div>
        </div>

        <!-- Talk Topics -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Talk Topics</span>
            <button class="btn btn-sm btn-secondary" onclick="loadAdminTopics()">Load</button>
          </div>
          <div class="card-body">
            <div id="topicsBox" style="overflow-x: auto;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch topics</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Debug Section -->
      <section class="section" id="sectionDebug">
        <div class="card">
          <div class="card-header">
            <span class="card-title">Debug Log</span>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-secondary" onclick="checkHealth()">Health</button>
              <button class="btn btn-sm btn-secondary" onclick="refreshState()">State</button>
              <button class="btn btn-sm btn-ghost" onclick="clearLog()">Clear</button>
            </div>
          </div>
          <div class="card-body">
            <div class="output" id="log">Ready...</div>
          </div>
        </div>
      </section>
    </main>
  </div>

<script>
  // State
  let sessionId = null;
  let lastQuestionId = null;
  let topicsCache = [];
  let activeTopicId = null;

  // Elements
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  const spinner = document.getElementById('spinner');
  const logEl = document.getElementById('log');

  // Helpers
  function log(obj) {
    const t = new Date().toLocaleTimeString();
    const s = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
    logEl.textContent = `[${t}] ${s}\n\n` + logEl.textContent;
  }

  function clearLog() { logEl.textContent = ''; }

  // Toast notification
  function toast(message, type = 'error', duration = 4000) {
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);

    setTimeout(() => {
      el.style.animation = 'slideOut 0.3s ease forwards';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  function setStatus(state, text) {
    statusDot.className = 'status-dot ' + state;
    statusText.textContent = text;
  }

  function showSpinner(show) { spinner.classList.toggle('show', show); }

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || res.statusText);
    return data;
  }

  async function fetchMultipart(url, formData) {
    const res = await fetch(url, { method: 'POST', body: formData });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || res.statusText);
    return data;
  }

  // Navigation
  function showSection(name) {
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelector(`[onclick="showSection('${name}')"]`).classList.add('active');
    document.getElementById('section' + name.charAt(0).toUpperCase() + name.slice(1)).classList.add('active');
  }

  // Health
  async function checkHealth() {
    showSpinner(true);
    try {
      const data = await fetchJson('/health');
      setStatus('ok', 'connected');
      log({ endpoint: '/health', data });
    } catch (e) {
      setStatus('error', 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // State
  async function refreshState() {
    try {
      const data = await fetchJson('/state');
      document.getElementById('statePhase').textContent = data.phase || '-';
      document.getElementById('stateQuestion').textContent = data.current_question || '-';
      log({ endpoint: '/state', data });
    } catch (e) {
      log({ error: e.message });
    }
  }

  // Session
  async function startSession() {
    const name = document.getElementById('visitorName').value.trim();
    if (!name) return log('visitor_name is empty');

    showSpinner(true);
    try {
      const data = await fetchJson('/session/start', {
        method: 'POST',
        body: JSON.stringify({ visitor_name: name })
      });
      sessionId = data.session_id;
      document.getElementById('sessionId').textContent = sessionId;
      log({ endpoint: '/session/start', data });
      toast('Session started', 'success', 2000);
      await refreshState();
    } catch (e) {
      toast(`Session start failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function endSession() {
    if (!sessionId) {
      toast('No active session', 'error');
      return log('No session');
    }
    showSpinner(true);
    try {
      const data = await fetchJson('/session/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, reason: 'completed' })
      });
      sessionId = null;
      activeTopicId = null;
      document.getElementById('sessionId').textContent = '-';
      document.getElementById('talkInput').disabled = true;
      document.getElementById('sendTalkBtn').disabled = true;
      log({ endpoint: '/session/end', data });
      toast('Session ended', 'info', 2000);
    } catch (e) {
      toast(`Session end failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Question
  async function getCurrentQuestion() {
    if (!sessionId) {
      toast('No session - please start a session first', 'error');
      return log('No session');
    }
    showSpinner(true);
    try {
      const data = await fetchJson(`/question/current?session_id=${sessionId}`);
      lastQuestionId = data.id;
      document.getElementById('qBadge').textContent = `question: ${data.id} (${data.session_question_index || '?'}/5)`;
      document.getElementById('questionText').textContent = data.question_text;
      document.getElementById('choiceA').textContent = data.choice_a;
      document.getElementById('choiceB').textContent = data.choice_b;
      document.getElementById('reactionBox').style.display = 'none';
      log({ endpoint: '/question/current', data });
    } catch (e) {
      toast(`Load question failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function sendAnswer(choice) {
    if (!sessionId || !lastQuestionId) {
      toast('No session or question loaded', 'error');
      return log('No session or question');
    }
    showSpinner(true);
    try {
      const data = await fetchJson('/answer', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, question_id: lastQuestionId, choice })
      });
      document.getElementById('reactionBox').style.display = 'block';
      document.getElementById('reactionText').textContent = data.assistant_reaction_text || 'OK';
      log({ endpoint: '/answer', data });
      if (data.session_should_end) {
        toast('Session completed! Click End to finish.', 'success', 5000);
        log('Session completed! Click End to finish.');
      }
      await refreshState();
    } catch (e) {
      toast(`Answer failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Idle Greeting & Monologue
  async function testIdleGreeting() {
    showSpinner(true);
    try {
      const data = await fetchJson('/idle/greeting');
      document.getElementById('stageBadge').textContent = `stage: ${data.stage_id} (${data.stage_name_kr})`;
      document.getElementById('idleStageInfo').textContent = `Stage ${data.stage_id}: ${data.stage_name_kr} (${data.stage_name_en}) | answered: ${data.answered_total}`;
      document.getElementById('idleResultText').textContent = data.greeting;
      document.getElementById('idleResultBox').style.display = 'block';
      log({ endpoint: '/idle/greeting', data });
      toast('Idle greeting loaded', 'success', 2000);
    } catch (e) {
      toast(`Idle greeting failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function testIdleMonologue() {
    showSpinner(true);
    try {
      const data = await fetchJson('/monologue', {
        method: 'POST',
        body: JSON.stringify({})
      });
      document.getElementById('stageBadge').textContent = `stage: ${data.stage_id} (${data.stage_name_kr})`;
      document.getElementById('idleStageInfo').textContent = `Stage ${data.stage_id}: ${data.stage_name_kr} (${data.stage_name_en}) | answered: ${data.answered_total}`;
      document.getElementById('idleResultText').textContent = data.monologue_text;
      document.getElementById('idleResultBox').style.display = 'block';
      log({ endpoint: '/monologue', data });
      toast('Monologue generated', 'success', 2000);
    } catch (e) {
      toast(`Monologue failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Topics
  async function loadTopics() {
    try {
      const data = await fetchJson('/talk/topics');
      topicsCache = data.topics || [];
      const sel = document.getElementById('topicSelect');
      sel.innerHTML = '';
      topicsCache.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = `${t.id}. ${t.title}`;
        sel.appendChild(opt);
      });
      log({ endpoint: '/talk/topics', count: topicsCache.length });
    } catch (e) {
      log({ error: e.message });
    }
  }

  // Talk
  function addChatMessage(role, text) {
    const el = document.createElement('div');
    el.className = 'message ' + role;
    el.textContent = text;
    document.getElementById('chatMessages').appendChild(el);
    el.scrollIntoView({ behavior: 'smooth' });
    return el;
  }

  async function talkStart() {
    if (!sessionId) {
      toast('No session - please start a session first', 'error');
      return log('No session');
    }
    const tid = parseInt(document.getElementById('topicSelect').value);
    showSpinner(true);
    try {
      const data = await fetchJson('/talk/start', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, topic_id: tid })
      });
      activeTopicId = tid;
      document.getElementById('chatMessages').innerHTML = '';
      addChatMessage('system', `Talk started (topic: ${tid})`);
      const first = data.assistant_first_text || data.ui_text || '';
      if (first) addChatMessage('assistant', first);
      document.getElementById('talkInput').disabled = false;
      document.getElementById('sendTalkBtn').disabled = false;
      log({ endpoint: '/talk/start', data });
      toast('Talk started', 'success', 2000);
    } catch (e) {
      toast(`Talk start failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function sendTalk() {
    const input = document.getElementById('talkInput');
    const text = input.value.trim();
    if (!text || !sessionId || !activeTopicId) return;

    addChatMessage('user', text);
    input.value = '';
    const typing = addChatMessage('assistant', '...');

    try {
      const data = await fetchJson('/talk/turn', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, topic_id: activeTopicId, user_text: text })
      });
      typing.textContent = data.ui_text || data.assistant_text || '';
      log({ endpoint: '/talk/turn', data });
    } catch (e) {
      typing.textContent = 'Error: ' + e.message;
      toast(`Message failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  async function talkEnd() {
    if (!sessionId) {
      toast('No session', 'error');
      return log('No session');
    }
    try {
      const data = await fetchJson('/talk/end', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId })
      });
      addChatMessage('system', 'Talk ended');
      document.getElementById('talkInput').disabled = true;
      document.getElementById('sendTalkBtn').disabled = true;
      activeTopicId = null;
      log({ endpoint: '/talk/end', data });
      toast('Talk ended', 'info', 2000);
    } catch (e) {
      toast(`Talk end failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  async function talkNudge() {
    if (!sessionId) {
      toast('No session - please start a session first', 'error');
      return log('No session');
    }
    if (!activeTopicId) {
      toast('No active talk - please start talk first', 'error');
      return log('No active talk');
    }

    const typing = addChatMessage('assistant', '(thinking...)');
    showSpinner(true);

    try {
      const data = await fetchJson('/monologue/nudge', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId })
      });
      typing.textContent = data.monologue_text || '';
      typing.style.fontStyle = 'italic';
      typing.style.opacity = '0.85';
      log({ endpoint: '/monologue/nudge', data });
      toast('Nudge sent', 'success', 2000);
    } catch (e) {
      typing.textContent = 'Nudge error: ' + e.message;
      toast(`Nudge failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  document.getElementById('talkInput').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTalk();
    }
  });

  // Admin
  async function fetchAdminProgress() {
    try {
      const data = await fetchJson('/admin/progress');
      document.getElementById('admAnswered').textContent = data.answered_count ?? '-';
      document.getElementById('admMax').textContent = data.max_questions ?? '-';
      document.getElementById('admRatio').textContent = Math.round((data.progress_ratio || 0) * 100) + '%';
      document.getElementById('admPhase').textContent = data.phase ?? '-';
      log({ endpoint: '/admin/progress', data });
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function fetchAdminSessions() {
    const limit = document.getElementById('admLimit').value;
    const offset = document.getElementById('admOffset').value;
    try {
      const data = await fetchJson(`/admin/sessions?limit=${limit}&offset=${offset}`);
      const sessions = data.sessions || [];
      let html = '<table><thead><tr><th>ID</th><th>Name</th><th>Started</th><th>Ended</th><th>Reason</th></tr></thead><tbody>';
      sessions.forEach(s => {
        html += `<tr><td>${s.id}</td><td>${s.visitor_name || ''}</td><td>${s.started_at || ''}</td><td>${s.ended_at || ''}</td><td>${s.end_reason || ''}</td></tr>`;
      });
      html += '</tbody></table>';
      document.getElementById('admSessionsBox').innerHTML = html;
      log({ endpoint: '/admin/sessions', total: data.total });
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function adminReset() {
    const body = {
      reset_answers: document.getElementById('resetAnswers').checked,
      reset_sessions: document.getElementById('resetSessions').checked,
      reset_state: document.getElementById('resetState').checked,
      reset_personality: document.getElementById('resetPersonality').checked
    };
    try {
      const data = await fetchJson('/admin/reset', { method: 'POST', body: JSON.stringify(body) });
      log({ endpoint: '/admin/reset', data });
      await refreshState();
      await fetchAdminProgress();
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function adminSetPhase() {
    const phase = document.getElementById('admPhaseSelect').value;
    try {
      const data = await fetchJson('/admin/phase/set', { method: 'POST', body: JSON.stringify({ phase }) });
      log({ endpoint: '/admin/phase/set', data });
      await refreshState();
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function adminSetCurrentQuestion() {
    const q = parseInt(document.getElementById('admSetQ').value);
    try {
      const data = await fetchJson('/admin/state/set_current_question', { method: 'POST', body: JSON.stringify({ current_question: q }) });
      log({ endpoint: '/admin/state/set_current_question', data });
      await refreshState();
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function adminImportQuestions() {
    const file = document.getElementById('admXlsxFile').files[0];
    if (!file) return log('No file selected');
    const fd = new FormData();
    fd.append('file', file);
    try {
      const data = await fetchMultipart('/admin/questions/import', fd);
      log({ endpoint: '/admin/questions/import', data });
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function adminImportSettings() {
    const file = document.getElementById('admSettingsXlsxFile').files[0];
    if (!file) return log('No file selected');
    const fd = new FormData();
    fd.append('file', file);
    try {
      const data = await fetchMultipart('/admin/settings/import', fd);
      log({ endpoint: '/admin/settings/import', data });
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function personaGenerate() {
    const body = {};
    const model = document.getElementById('personaModel').value;
    const maxTokens = document.getElementById('personaMaxTokens').value;
    if (model) body.model = model;
    if (maxTokens) body.max_output_tokens = parseInt(maxTokens);
    if (document.getElementById('personaForce').checked) body.force = true;

    showSpinner(true);
    toast(`Generating persona with ${model}...`, 'info', 3000);
    try {
      const data = await fetchJson('/persona/generate', { method: 'POST', body: JSON.stringify(body) });
      log({ endpoint: '/persona/generate', data });
      toast('Persona generated successfully', 'success');
      await refreshState();
    } catch (e) {
      toast(`Persona generation failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function fetchAdminPersonality() {
    try {
      const data = await fetchJson('/admin/personality');
      document.getElementById('pSelfDirection').value = data.self_direction ?? 0;
      document.getElementById('pConformity').value = data.conformity ?? 0;
      document.getElementById('pStimulation').value = data.stimulation ?? 0;
      document.getElementById('pSecurity').value = data.security ?? 0;
      document.getElementById('pHedonism').value = data.hedonism ?? 0;
      document.getElementById('pTradition').value = data.tradition ?? 0;
      document.getElementById('pAchievement').value = data.achievement ?? 0;
      document.getElementById('pBenevolence').value = data.benevolence ?? 0;
      document.getElementById('pPower').value = data.power ?? 0;
      document.getElementById('pUniversalism').value = data.universalism ?? 0;
      log({ endpoint: '/admin/personality', data });
    } catch (e) {
      log({ error: e.message });
    }
  }

  async function adminSetPersonality() {
    const body = {
      self_direction: parseInt(document.getElementById('pSelfDirection').value) || 0,
      conformity: parseInt(document.getElementById('pConformity').value) || 0,
      stimulation: parseInt(document.getElementById('pStimulation').value) || 0,
      security: parseInt(document.getElementById('pSecurity').value) || 0,
      hedonism: parseInt(document.getElementById('pHedonism').value) || 0,
      tradition: parseInt(document.getElementById('pTradition').value) || 0,
      achievement: parseInt(document.getElementById('pAchievement').value) || 0,
      benevolence: parseInt(document.getElementById('pBenevolence').value) || 0,
      power: parseInt(document.getElementById('pPower').value) || 0,
      universalism: parseInt(document.getElementById('pUniversalism').value) || 0
    };
    try {
      const data = await fetchJson('/admin/personality/set', { method: 'POST', body: JSON.stringify(body) });
      log({ endpoint: '/admin/personality/set', data });
    } catch (e) {
      log({ error: e.message });
    }
  }

  // Config Management
  let configsCache = [];

  async function loadConfigs() {
    showSpinner(true);
    try {
      const data = await fetchJson('/admin/config');
      configsCache = data.configs || [];
      renderConfigTable();
      log({ endpoint: '/admin/config', count: configsCache.length });
      toast('Configs loaded', 'success', 2000);
    } catch (e) {
      toast(`Load configs failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  function renderConfigTable() {
    const box = document.getElementById('configTableBox');
    if (!configsCache.length) {
      box.innerHTML = '<div style="color: var(--muted);">No configs found</div>';
      return;
    }

    let html = `<table style="width: 100%; font-size: 12px; border-collapse: collapse;">
      <thead>
        <tr style="border-bottom: 1px solid var(--border); text-align: left;">
          <th style="padding: 8px 4px;">Key</th>
          <th style="padding: 8px 4px;">Value</th>
          <th style="padding: 8px 4px;">Type</th>
          <th style="padding: 8px 4px; width: 80px;">Action</th>
        </tr>
      </thead>
      <tbody>`;

    for (const c of configsCache) {
      const inputType = (c.type === 'int' || c.type === 'float') ? 'number' : 'text';
      const step = c.type === 'float' ? 'step="0.01"' : '';
      html += `<tr style="border-bottom: 1px solid var(--border);">
        <td style="padding: 6px 4px; font-family: var(--mono); font-size: 11px;" title="${c.description || ''}">${c.key}</td>
        <td style="padding: 6px 4px;">
          <input type="${inputType}" ${step} id="cfg_${c.key}" value="${escapeHtml(c.value)}" style="width: 100%; font-size: 11px;" />
        </td>
        <td style="padding: 6px 4px; color: var(--muted);">${c.type}</td>
        <td style="padding: 6px 4px;">
          <button class="btn btn-sm btn-secondary" onclick="saveConfig('${c.key}')">Save</button>
        </td>
      </tr>`;
    }

    html += '</tbody></table>';
    box.innerHTML = html;
  }

  function escapeHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  async function saveConfig(key) {
    const input = document.getElementById('cfg_' + key);
    if (!input) return;
    const value = input.value;

    try {
      const data = await fetchJson(`/admin/config/${encodeURIComponent(key)}?value=${encodeURIComponent(value)}`, { method: 'PUT' });
      log({ endpoint: `/admin/config/${key}`, data });
      toast(`Config "${key}" saved`, 'success', 2000);
    } catch (e) {
      toast(`Save config failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  async function clearConfigCache() {
    try {
      const data = await fetchJson('/admin/config/clear-cache', { method: 'POST' });
      log({ endpoint: '/admin/config/clear-cache', data });
      toast('Config cache cleared', 'success', 2000);
    } catch (e) {
      toast(`Clear cache failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  // Prompts Management
  let promptsCache = [];

  // 변수 정의: { var: description }
  const PROMPT_VARS = {
    'reaction_prompt': {
      '{stage_name}': '성장단계 이름 (태동기, 형성기 등)',
      '{style_guide}': '스타일 가이드 (은유적으로, 조심스럽게 등)',
      '{notes_line}': '[말투 예시: xxx] 또는 빈 문자열',
      '{question_text}': '현재 질문 텍스트',
      '{choice}': '사용자 선택 (A 또는 B)',
      '{session_question_index}': '세션 내 질문 번호 (1~5)',
      '{session_question_limit}': '세션당 최대 질문 수',
      '{last_instruction}': '마지막 여부에 따른 안내문',
    },
    'persona_prompt': {
      '{values_summary}': '가치 축 결과 텍스트 요약',
      '{pair_insights}': '페어별 상세 분석 JSON',
    },
    'persona_fallback': {}
  };

  async function loadPrompts() {
    showSpinner(true);
    try {
      const data = await fetchJson('/admin/prompts');
      promptsCache = data.prompts || [];
      renderPromptSelect();
      log({ endpoint: '/admin/prompts', count: promptsCache.length });
      toast('Prompts loaded', 'success', 2000);
    } catch (e) {
      toast(`Load prompts failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  function renderPromptSelect() {
    const sel = document.getElementById('promptSelect');
    sel.innerHTML = '<option value="">-- Select prompt --</option>';
    for (const p of promptsCache) {
      sel.innerHTML += `<option value="${p.key}">${p.key} - ${p.description || ''}</option>`;
    }
  }

  function onPromptSelect() {
    const key = document.getElementById('promptSelect').value;
    const textarea = document.getElementById('promptTemplate');
    const varsBox = document.getElementById('promptVarsBox');
    const varsButtons = document.getElementById('promptVarButtons');

    if (!key) {
      textarea.value = '';
      varsBox.style.display = 'none';
      return;
    }

    const p = promptsCache.find(x => x.key === key);
    if (p) {
      textarea.value = p.template || '';
    }

    // 변수 버튼 렌더링
    const vars = PROMPT_VARS[key] || {};
    const varKeys = Object.keys(vars);

    if (varKeys.length > 0) {
      varsBox.style.display = 'block';
      varsButtons.innerHTML = varKeys.map(v =>
        `<span class="var-tag" onclick="insertVar('${v}')" title="${vars[v]}">${v}</span>`
      ).join('');
    } else {
      varsBox.style.display = 'none';
      varsButtons.innerHTML = '';
    }
  }

  function insertVar(varName) {
    const textarea = document.getElementById('promptTemplate');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;

    textarea.value = text.substring(0, start) + varName + text.substring(end);
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = start + varName.length;
  }

  async function savePrompt() {
    const key = document.getElementById('promptSelect').value;
    if (!key) {
      toast('Select a prompt first', 'error');
      return;
    }

    const template = document.getElementById('promptTemplate').value;

    try {
      const data = await fetchJson(`/admin/prompts/${encodeURIComponent(key)}?template=${encodeURIComponent(template)}`, { method: 'PUT' });
      log({ endpoint: `/admin/prompts/${key}`, data });
      toast(`Prompt "${key}" saved`, 'success', 2000);
      // Update cache
      const idx = promptsCache.findIndex(x => x.key === key);
      if (idx >= 0) promptsCache[idx].template = template;
    } catch (e) {
      toast(`Save prompt failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  async function clearPromptCache() {
    try {
      const data = await fetchJson('/admin/prompts/clear-cache', { method: 'POST' });
      log({ endpoint: '/admin/prompts/clear-cache', data });
      toast('Prompt cache cleared', 'success', 2000);
    } catch (e) {
      toast(`Clear cache failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  // Quick Test
  async function runQuickTest() {
    const name = document.getElementById('quickTestName').value || 'QuickTest';
    const count = document.getElementById('quickTestCount').value || 5;

    showSpinner(true);
    toast('Running quick test...', 'info', 2000);

    try {
      const data = await fetchJson(`/admin/quick-test?visitor_name=${encodeURIComponent(name)}&answer_count=${count}`, {
        method: 'POST'
      });

      const resultBox = document.getElementById('quickTestResult');
      resultBox.style.display = 'block';
      resultBox.innerHTML = `
        <div style="color: var(--accent); margin-bottom: 8px;">✓ Quick Test 완료</div>
        <div>Session ID: ${data.session_id}</div>
        <div>Answers: ${data.answers_count}개</div>
        <div>Start Q: ${data.start_question_id} → Next Q: ${data.next_question_id}</div>
        <div style="margin-top: 8px; color: var(--muted);">
          ${data.answers.map(a => `Q${a.question_id}: ${a.choice} (${a.chosen_value_key})`).join(' | ')}
        </div>
      `;

      log({ endpoint: '/admin/quick-test', data });
      toast('Quick test completed', 'success');
      await refreshState();
      await fetchAdminProgress();
    } catch (e) {
      toast(`Quick test failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Current Persona
  async function loadCurrentPersona() {
    showSpinner(true);
    try {
      const data = await fetchJson('/admin/persona');

      document.getElementById('personaInfoBox').innerHTML = `
        <span class="badge ${data.phase === 'talk' ? 'badge-success' : ''}">${data.phase}</span>
        <span style="margin-left: 8px;">formed_at: ${data.formed_at || 'N/A'}</span>
        <span style="margin-left: 8px;">current_question: ${data.current_question || 'N/A'}</span>
      `;

      const promptBox = document.getElementById('personaPromptBox');
      promptBox.style.display = 'block';

      document.getElementById('personaValuesSummary').textContent = data.values_summary || '(not generated)';
      document.getElementById('personaPromptText').textContent = data.persona_prompt || '(not generated)';

      log({ endpoint: '/admin/persona', phase: data.phase, formed_at: data.formed_at });
      toast('Persona loaded', 'success', 2000);
    } catch (e) {
      toast(`Load persona failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Questions List
  async function loadQuestions() {
    const limit = document.getElementById('questionsLimit').value || 20;
    const offset = document.getElementById('questionsOffset').value || 0;
    const enabledOnly = document.getElementById('questionsEnabledOnly').checked;

    showSpinner(true);
    try {
      const data = await fetchJson(`/admin/questions?limit=${limit}&offset=${offset}&enabled_only=${enabledOnly}`);

      const box = document.getElementById('questionsBox');
      if (!data.questions || data.questions.length === 0) {
        box.innerHTML = '<div style="color: var(--muted);">No questions found</div>';
        return;
      }

      let html = `<div style="margin-bottom: 8px; font-size: 12px; color: var(--muted);">Total: ${data.total}</div>`;
      html += `<table style="width: 100%; font-size: 11px;"><thead><tr>
        <th style="padding: 6px;">ID</th>
        <th style="padding: 6px;">Question</th>
        <th style="padding: 6px;">A</th>
        <th style="padding: 6px;">B</th>
        <th style="padding: 6px;">Enabled</th>
      </tr></thead><tbody>`;

      for (const q of data.questions) {
        const enabledClass = q.enabled ? 'badge-success' : '';
        html += `<tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 6px; font-family: var(--mono);">${q.id}</td>
          <td style="padding: 6px; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(q.question_text)}">${escapeHtml(q.question_text)}</td>
          <td style="padding: 6px; font-size: 10px; color: var(--muted);">${q.value_a_key || ''}</td>
          <td style="padding: 6px; font-size: 10px; color: var(--muted);">${q.value_b_key || ''}</td>
          <td style="padding: 6px;">
            <button class="btn btn-sm ${q.enabled ? 'btn-primary' : 'btn-ghost'}" onclick="toggleQuestion(${q.id})">${q.enabled ? 'ON' : 'OFF'}</button>
          </td>
        </tr>`;
      }
      html += '</tbody></table>';
      box.innerHTML = html;

      log({ endpoint: '/admin/questions', total: data.total, shown: data.questions.length });
    } catch (e) {
      toast(`Load questions failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function toggleQuestion(id) {
    try {
      const data = await fetchJson(`/admin/questions/${id}/toggle`, { method: 'PUT' });
      toast(`Question ${id} ${data.enabled ? 'enabled' : 'disabled'}`, 'success', 2000);
      await loadQuestions();
    } catch (e) {
      toast(`Toggle failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  // Growth Stages
  async function loadGrowthStages() {
    showSpinner(true);
    try {
      const data = await fetchJson('/admin/growth-stages');

      const box = document.getElementById('growthStagesBox');
      if (!data.stages || data.stages.length === 0) {
        box.innerHTML = '<div style="color: var(--muted);">No stages found</div>';
        return;
      }

      let html = `<table style="width: 100%; font-size: 11px;"><thead><tr>
        <th style="padding: 6px;">ID</th>
        <th style="padding: 6px;">Name</th>
        <th style="padding: 6px;">Range</th>
        <th style="padding: 6px;">Idle Greeting</th>
      </tr></thead><tbody>`;

      for (const s of data.stages) {
        const greeting = s.idle_greeting ? s.idle_greeting.substring(0, 50) + '...' : '(empty)';
        html += `<tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 6px; font-family: var(--mono);">${s.stage_id}</td>
          <td style="padding: 6px;">${s.stage_name_kr} (${s.stage_name_en})</td>
          <td style="padding: 6px; font-family: var(--mono);">${s.min_answers} ~ ${s.max_answers}</td>
          <td style="padding: 6px; font-size: 10px; color: var(--muted); max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(s.idle_greeting || '')}">${escapeHtml(greeting)}</td>
        </tr>`;
      }
      html += '</tbody></table>';
      box.innerHTML = html;

      log({ endpoint: '/admin/growth-stages', count: data.stages.length });
      toast('Growth stages loaded', 'success', 2000);
    } catch (e) {
      toast(`Load stages failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Talk Topics (Admin)
  async function loadAdminTopics() {
    showSpinner(true);
    try {
      const data = await fetchJson('/admin/topics');

      const box = document.getElementById('topicsBox');
      if (!data.topics || data.topics.length === 0) {
        box.innerHTML = '<div style="color: var(--muted);">No topics found</div>';
        return;
      }

      let html = `<table style="width: 100%; font-size: 12px;"><thead><tr>
        <th style="padding: 8px;">ID</th>
        <th style="padding: 8px;">Title</th>
        <th style="padding: 8px;">Description</th>
      </tr></thead><tbody>`;

      for (const t of data.topics) {
        html += `<tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 8px; font-family: var(--mono);">${t.id}</td>
          <td style="padding: 8px; font-weight: 500;">${escapeHtml(t.title)}</td>
          <td style="padding: 8px; color: var(--muted); font-size: 11px;">${escapeHtml(t.description || '')}</td>
        </tr>`;
      }
      html += '</tbody></table>';
      box.innerHTML = html;

      log({ endpoint: '/admin/topics', count: data.topics.length });
      toast('Topics loaded', 'success', 2000);
    } catch (e) {
      toast(`Load topics failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Help Modal
  const HELP_CONTENT = {
    general: `
      <div class="help-section">
        <h4>📌 개요</h4>
        <p>Psano Console은 전시 작품 '사노'의 백엔드 테스트 및 관리 도구입니다.</p>
        <p>사노는 관람객의 선택(A/B 질문)을 통해 성격이 형성되고, 이후 대화를 나눌 수 있는 AI 캐릭터입니다.</p>
      </div>
      <div class="help-section">
        <h4>🔄 기본 흐름</h4>
        <ul>
          <li><strong>Session Start</strong> → 방문자 이름 입력 후 세션 시작</li>
          <li><strong>Formation</strong> → A/B 질문 5개 응답 (성격 형성)</li>
          <li><strong>Session End</strong> → 세션 종료 (personality 반영)</li>
          <li><strong>Talk</strong> → 380문항 완료 후 대화 가능</li>
        </ul>
      </div>
    `,
    formation: `
      <div class="help-section">
        <h4>📝 Formation (A/B 질문)</h4>
        <p>관람객이 A 또는 B 중 하나를 선택하면, 해당 가치(value)가 사노의 성격에 반영됩니다.</p>
        <ul>
          <li><strong>Load Question</strong>: 현재 세션의 질문 불러오기</li>
          <li><strong>A / B 버튼</strong>: 선택 제출 → 사노의 반응 표시</li>
          <li>세션당 5문항 응답 후 자동으로 세션 종료 안내</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>🌱 Idle State (인사/혼잣말)</h4>
        <p>TouchDesigner에서 idle 상태의 사노를 클릭했을 때 사용하는 API 테스트입니다.</p>
        <ul>
          <li><strong>Idle Greeting</strong>: 성장단계별 고정 인사말 (DB에서 로드)</li>
          <li><strong>Idle Monologue</strong>: LLM이 성장단계 스타일로 혼잣말 생성</li>
        </ul>
        <p style="color: var(--muted); font-size: 12px;">* 성장단계는 총 답변 수(answered_total)에 따라 1~6단계로 나뉩니다.</p>
      </div>
    `,
    talk: `
      <div class="help-section">
        <h4>💬 Talk (대화)</h4>
        <p>380문항 형성 완료 후 사노와 자유 대화를 나눌 수 있습니다.</p>
        <ul>
          <li><strong>Load Topics</strong>: 대화 주제 목록 불러오기</li>
          <li><strong>Start Talk</strong>: 선택한 주제로 대화 시작</li>
          <li><strong>Nudge</strong>: 사용자 반응 없을 때 사노가 툭 던지는 한마디</li>
          <li><strong>End Talk</strong>: 대화 종료</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>⚠️ 주의사항</h4>
        <ul>
          <li>Talk은 phase가 'talk'일 때만 시작 가능</li>
          <li>Nudge는 Talk이 활성화된 상태에서만 동작</li>
          <li>정책 규칙(자해/개인정보 등)에 의해 응답이 필터링될 수 있음</li>
        </ul>
      </div>
    `,
    admin: `
      <div class="help-section">
        <h4>⚙️ Admin (관리)</h4>
        <p>시스템 상태 확인 및 데이터 관리 기능입니다.</p>
      </div>
      <div class="help-section">
        <h4>📊 Progress</h4>
        <p>현재 답변 진행률과 phase 확인</p>
      </div>
      <div class="help-section">
        <h4>🔄 Reset</h4>
        <p>선택한 데이터 초기화 (answers, sessions, state, personality)</p>
      </div>
      <div class="help-section">
        <h4>🎭 Persona Generate</h4>
        <p>380문항 완료 후 LLM으로 사노의 persona_prompt 생성</p>
        <ul>
          <li><strong>Model</strong>: 사용할 GPT 모델 선택</li>
          <li><strong>force</strong>: 기존 persona가 있어도 재생성</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>📝 Config / Prompts</h4>
        <p>DB에 저장된 설정값과 프롬프트 템플릿 관리</p>
        <ul>
          <li><strong>Config</strong>: 임계값, 최대값 등 시스템 설정</li>
          <li><strong>Prompts</strong>: LLM 프롬프트 템플릿 (변수 클릭으로 삽입)</li>
        </ul>
      </div>
    `,
    debug: `
      <div class="help-section">
        <h4>🔍 Debug</h4>
        <p>API 호출 로그 및 시스템 상태 확인용입니다.</p>
        <ul>
          <li><strong>Health</strong>: 서버 연결 상태 확인</li>
          <li><strong>State</strong>: 현재 phase, current_question 확인</li>
          <li><strong>Clear</strong>: 로그 지우기</li>
        </ul>
        <p style="color: var(--muted); font-size: 12px;">* 모든 API 호출 결과가 여기에 기록됩니다.</p>
      </div>
    `
  };

  function showHelp(section = null) {
    const modal = document.getElementById('helpModal');
    const body = document.getElementById('helpModalBody');

    // 현재 활성 섹션 감지
    if (!section) {
      const activeNav = document.querySelector('.nav-item.active');
      if (activeNav) {
        const onclick = activeNav.getAttribute('onclick') || '';
        const match = onclick.match(/showSection\('(\w+)'\)/);
        section = match ? match[1] : 'general';
      } else {
        section = 'general';
      }
    }

    // 콘텐츠 로드
    let content = HELP_CONTENT.general;
    if (HELP_CONTENT[section]) {
      content += HELP_CONTENT[section];
    }

    body.innerHTML = content;
    modal.classList.add('show');
  }

  function closeHelpModal(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('helpModal').classList.remove('show');
  }

  // ESC 키로 모달 닫기
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeHelpModal();
    }
  });

  // Init
  checkHealth();
  refreshState();
  loadTopics();
  fetchAdminProgress();
</script>

</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
def ui():
    return HTMLResponse(content=HTML)