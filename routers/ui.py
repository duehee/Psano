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
      max-width: 1200px;
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
      max-height: 400px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }

    /* Scrollable content box */
    .scroll-box {
      max-height: 300px;
      overflow-y: auto;
      padding: 12px;
      background: var(--secondary);
      border-radius: var(--radius-sm);
    }

    .scroll-box-dark {
      max-height: 350px;
      overflow-y: auto;
      padding: 16px;
      background: #1e293b;
      color: #e2e8f0;
      border-radius: var(--radius-sm);
      font-family: var(--mono);
      font-size: 12px;
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
      .grid-2 { grid-template-columns: 1fr; }
      .grid-3 { grid-template-columns: 1fr; }
      .grid-5 { grid-template-columns: 1fr 1fr; }
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
        <button class="nav-item" onclick="showSection('data')">
          <span class="icon">📊</span> Data
        </button>
        <button class="nav-item" onclick="showSection('settings')">
          <span class="icon">🔧</span> Settings
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
            <div style="display: flex; gap: 8px; margin-bottom: 16px; align-items: center; flex-wrap: wrap;">
              <button class="btn btn-primary" onclick="testIdleGreeting()">Idle Greeting (인사말)</button>
              <button class="btn btn-secondary" onclick="testIdleMonologue()">Idle Monologue (혼잣말)</button>
              <button class="btn btn-secondary" onclick="testIdleRandom()">Idle Random (가치축)</button>
              <button class="btn btn-secondary" onclick="testNudge()" title="대화 중 반응 없을 때 사노가 던지는 한마디 (Talk 세션 필요)">Nudge (찔러보기)</button>
              <select id="monologueModel" style="padding: 8px; border-radius: 6px; border: 1px solid var(--border);">
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4o-mini">gpt-4o-mini</option>
                <option value="gpt-4.1-mini">gpt-4.1-mini</option>
                <option value="gpt-5-mini">gpt-5-mini</option>
                <option value="gpt-5.2">gpt-5.2</option>
              </select>
            </div>
            <div id="idleResultBox" style="padding: 20px; background: var(--secondary); border-radius: 8px; display: none;">
              <div style="font-size: 12px; color: var(--muted); margin-bottom: 8px;">
                <span id="idleStageInfo">-</span>
              </div>
              <div id="idleResultText" style="font-size: 15px; line-height: 1.8; white-space: pre-wrap;"></div>
              <div style="margin-top: 12px;">
                <button class="btn btn-primary btn-sm" onclick="goToTalk()" id="btnGoToTalk" style="display: none;">이 혼잣말로 대화 시작 →</button>
              </div>
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

      <!-- Talk Section (혼잣말 기반 대화) -->
      <section class="section" id="sectionTalk">
        <div class="card">
          <div class="card-header">
            <span class="card-title">Talk (대화)</span>
            <div style="display: flex; gap: 8px;">
              <select id="talkModel" style="padding: 6px; border-radius: 6px; border: 1px solid var(--border);">
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4o-mini">gpt-4o-mini</option>
                <option value="gpt-4.1-mini">gpt-4.1-mini</option>
                <option value="gpt-5-mini">gpt-5-mini</option>
                <option value="gpt-5.2">gpt-5.2</option>
              </select>
              <button class="btn btn-sm btn-danger" onclick="endTalk()">End Talk</button>
            </div>
          </div>
          <div class="card-body">
            <!-- 선택된 혼잣말 표시 -->
            <div id="selectedIdleBox" style="padding: 16px; background: var(--secondary); border-radius: 8px; margin-bottom: 16px;">
              <div style="font-size: 12px; color: var(--muted); margin-bottom: 4px;">선택된 혼잣말</div>
              <div id="selectedIdleText" style="font-size: 14px;">혼잣말을 선택하세요 (Formation → Idle Random)</div>
            </div>
            <!-- 대화 시작 버튼 -->
            <div style="margin-bottom: 16px;">
              <button class="btn btn-primary" onclick="startTalk()" id="btnStartTalk">대화 시작</button>
            </div>
            <!-- 채팅 영역 -->
            <div class="chat-container" id="talkChatArea" style="display: none;">
              <!-- 턴 카운트 & 로컬 엔딩 정보 -->
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                  <span class="badge" id="talkTurnBadge">Turn: 0/50</span>
                  <span class="badge" id="talkRemainingBadge" style="background: #10b981; color: white;">남은 턴: 50</span>
                  <span class="badge badge-warning" id="talkLocalWarningBadge" style="display: none;">종료 임박</span>
                  <span class="badge" id="talkAskContinueBadge" style="display: none; background: #8b5cf6; color: white;">질문 트리거</span>
                  <span class="badge badge-warning" id="talkPolicyBadge" style="display: none;">정책 가이드</span>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <span class="badge" id="talkTimeoutBadge" style="background: #6b7280; color: white;">타임아웃: --:--</span>
                  <span style="font-size: 11px; color: var(--muted);" id="talkStatusText"></span>
                </div>
              </div>
              <div class="chat-messages" id="chatMessages" style="height: 320px; overflow-y: auto; padding: 16px; background: var(--secondary); border-radius: 8px; margin-bottom: 12px;">
                <div class="message system">대화가 시작되면 여기에 표시됩니다</div>
              </div>
              <div class="chat-input-bar" style="display: flex; gap: 8px;">
                <input type="text" id="talkInput" placeholder="메시지를 입력하세요..." style="flex: 1; padding: 12px; border-radius: 8px; border: 1px solid var(--border);" onkeypress="if(event.key==='Enter') sendTalk()">
                <button class="btn btn-primary" onclick="sendTalk()">Send</button>
                <button class="btn btn-secondary" onclick="sendNudge()" title="사노가 먼저 말 걸기">Nudge</button>
              </div>
              <!-- 글로벌 예고/엔딩 표시 -->
              <div id="globalWarningBox" style="display: none; margin-top: 12px; padding: 12px; background: #fef3c7; border-radius: 8px; color: #92400e; font-size: 13px;">
                <strong>⚠️ 예고:</strong> <span id="globalWarningText"></span>
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
                <div class="stat-value" id="admMax">365</div>
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
              <div class="stat">
                <div class="stat-value" id="admGlobalTurn">-</div>
                <div class="stat-label">Global Turns</div>
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

        <!-- State Control + Persona Generate (50:50) -->
        <div class="grid-2">
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

          <!-- Persona -->
          <div class="card">
            <div class="card-header">
              <span class="card-title">Persona Generate</span>
            </div>
            <div class="card-body">
              <div class="form-row" style="align-items: center;">
                <div class="form-group" style="flex: 1; margin-bottom: 0;">
                  <label class="checkbox" style="align-items: flex-start;">
                    <input type="checkbox" id="personaForce" />
                    <span>force (기존 persona 재생성)</span>
                  </label>
                </div>
                <div class="form-group" style="flex: 1; margin-bottom: 0;">
                  <button class="btn btn-primary" style="width: 100%;" onclick="personaGenerate()">페르소나 생성</button>
                </div>
              </div>
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
      </section>

      <!-- Data Section -->
      <section class="section" id="sectionData">
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
            <div id="questionsBox" style="overflow: auto; max-height: 350px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch questions</div>
            </div>
          </div>
        </div>

        <!-- Idle List -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Idle List (혼잣말 목록)</span>
            <div style="display: flex; gap: 8px; align-items: center;">
              <label class="checkbox" style="font-size: 12px;"><input type="checkbox" id="idleEnabledOnly" /> enabled only</label>
              <input type="number" id="idleLimit" value="30" style="width: 50px;" placeholder="limit" />
              <input type="number" id="idleOffset" value="0" style="width: 50px;" placeholder="offset" />
              <button class="btn btn-sm btn-secondary" onclick="loadIdleList()">Load</button>
            </div>
          </div>
          <div class="card-body">
            <div id="idleListBox" style="overflow: auto; max-height: 350px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch idle list</div>
            </div>
          </div>
        </div>

        <!-- Policy Rules -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Policy Rules (정책 필터)</span>
            <div style="display: flex; gap: 8px; align-items: center;">
              <label class="checkbox" style="font-size: 12px;"><input type="checkbox" id="policyEnabledOnly" /> enabled only</label>
              <button class="btn btn-sm btn-secondary" onclick="loadPolicyRules()">Load</button>
            </div>
          </div>
          <div class="card-body">
            <div id="policyRulesBox" style="overflow: auto; max-height: 350px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch policy rules</div>
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
            <div id="growthStagesBox" style="overflow: auto; max-height: 300px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch growth stages</div>
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
            <div id="admSessionsBox" style="overflow: auto; max-height: 300px;">
              <div style="color: var(--muted); font-size: 13px;">Click Load to fetch sessions</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Settings Section -->
      <section class="section" id="sectionSettings">
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

        <!-- Import -->
        <div class="card">
          <div class="card-header">
            <span class="card-title">Import</span>
          </div>
          <div class="card-body">
            <div class="grid-2" style="gap: 16px;">
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
              <div class="form-group">
                <label class="form-label">Idle (xlsx)</label>
                <input type="file" id="admIdleXlsxFile" accept=".xlsx" />
                <button class="btn btn-primary btn-sm" style="margin-top: 8px;" onclick="adminImportIdle()">Upload</button>
              </div>
              <div class="form-group">
                <label class="form-label">Policy Rules (xlsx)</label>
                <input type="file" id="admPolicyRulesXlsxFile" accept=".xlsx" />
                <button class="btn btn-primary btn-sm" style="margin-top: 8px;" onclick="adminImportPolicyRules()">Upload</button>
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
              <div id="personaValuesSummary" class="scroll-box" style="font-size: 12px; margin-bottom: 12px; white-space: pre-wrap; max-height: 200px;"></div>
              <div class="form-label">Persona Prompt</div>
              <div id="personaPromptText" class="scroll-box-dark"></div>
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
  let currentIdleId = null;    // 현재 선택된 idle ID
  let currentIdleText = null;  // 현재 선택된 혼잣말 텍스트
  let talkTurnCount = 0;       // 현재 세션 대화 턴 수
  let nudgeTimerId = null;     // auto-nudge 타이머 ID
  let nudgeFiredThisTurn = false; // 현재 턴에서 nudge 발동 여부
  const NUDGE_TIMEOUT = 15000; // 15초

  // 로컬 엔딩 관련
  let localEndTurnCount = 50;      // 세션당 최대 턴 (config에서 로드)
  let localWarningThreshold = 5;   // 예고 시작 잔여 턴
  let localAskInterval = 10;       // N턴마다 질문
  let sessionIdleTimeoutSec = 300; // 세션 타임아웃 (초)
  let sessionTimeoutTimerId = null; // 세션 타임아웃 타이머 ID
  let sessionTimeoutRemaining = 0;  // 남은 타임아웃 (초)

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
      currentIdleId = null;
      currentIdleText = null;
      document.getElementById('sessionId').textContent = '-';
      // Talk UI 리셋
      document.getElementById('talkChatArea').style.display = 'none';
      document.getElementById('btnStartTalk').style.display = 'inline-block';
      document.getElementById('chatMessages').innerHTML = '<div class="message system">대화가 시작되면 여기에 표시됩니다</div>';
      document.getElementById('selectedIdleText').textContent = '혼잣말을 선택하세요 (Formation → Idle Random)';
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
    const model = document.getElementById('monologueModel').value;
    try {
      const data = await fetchJson('/monologue', {
        method: 'POST',
        body: JSON.stringify({ model: model })
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

  async function testIdleRandom() {
    showSpinner(true);
    try {
      const data = await fetchJson('/idle/random');
      currentIdleId = data.id;
      currentIdleText = data.text;
      document.getElementById('idleStageInfo').textContent = `axis_key: ${data.axis_key} | id: ${data.id}`;
      document.getElementById('idleResultText').textContent = data.text;
      document.getElementById('idleResultBox').style.display = 'block';
      document.getElementById('btnGoToTalk').style.display = 'inline-block';
      // Talk 섹션에도 표시
      document.getElementById('selectedIdleText').textContent = data.text;
      log({ endpoint: '/idle/random', data });
      toast('Idle random loaded', 'success', 2000);
    } catch (e) {
      toast(`Idle random failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function testNudge() {
    if (!sessionId) {
      toast('Talk 세션이 필요합니다. Talk 탭에서 대화를 시작하세요.', 'error');
      return;
    }
    showSpinner(true);
    const model = document.getElementById('monologueModel').value;
    try {
      const data = await fetchJson('/monologue/nudge', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, model: model })
      });
      document.getElementById('idleStageInfo').textContent = `session: ${data.session_id} | idle_id: ${data.idle_id}`;
      document.getElementById('idleResultText').textContent = data.nudge_text;
      document.getElementById('idleResultBox').style.display = 'block';
      document.getElementById('btnGoToTalk').style.display = 'none';
      log({ endpoint: '/monologue/nudge', data });
      toast('Nudge generated', 'success', 2000);
    } catch (e) {
      toast(`Nudge failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Talk 섹션으로 이동
  function goToTalk() {
    if (!currentIdleId) {
      toast('먼저 Idle Random을 실행하세요', 'error');
      return;
    }
    showSection('talk');
  }

  // Talk (대화)
  // Auto-nudge 타이머 관리
  function clearNudgeTimer() {
    if (nudgeTimerId) {
      clearTimeout(nudgeTimerId);
      nudgeTimerId = null;
    }
  }

  function startNudgeTimer() {
    clearNudgeTimer();
    // 이미 이번 턴에서 nudge 발동했으면 타이머 시작 안 함
    if (nudgeFiredThisTurn) return;
    nudgeTimerId = setTimeout(async () => {
      if (!sessionId || !currentIdleId) return;
      // 자동 nudge 발동
      toast('15초간 응답 없음 - Nudge 발동', 'info', 2000);
      await triggerAutoNudge();
    }, NUDGE_TIMEOUT);
  }

  async function triggerAutoNudge() {
    if (!sessionId) return;
    nudgeFiredThisTurn = true; // 이번 턴에서 nudge 발동 표시
    const model = document.getElementById('talkModel').value;
    try {
      const data = await fetchJson('/monologue/nudge', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId, model: model })
      });
      addChatMessage('system', '[auto-nudge]');
      addChatMessage('assistant', data.nudge_text);
      log({ endpoint: '/monologue/nudge (auto)', data });
      // 턴당 1회만 발동하므로 타이머 재시작 안 함
    } catch (e) {
      toast(`Auto-nudge failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  // 로컬 엔딩 config 로드
  async function loadLocalEndingConfig() {
    try {
      const data = await fetchJson('/admin/config');
      for (const cfg of data.configs || []) {
        if (cfg.key === 'local_end_turn_count') localEndTurnCount = parseInt(cfg.value) || 50;
        if (cfg.key === 'local_warning_threshold') localWarningThreshold = parseInt(cfg.value) || 5;
        if (cfg.key === 'local_ask_interval') localAskInterval = parseInt(cfg.value) || 10;
        if (cfg.key === 'session_idle_timeout_sec') sessionIdleTimeoutSec = parseInt(cfg.value) || 300;
      }
      log({ localEndingConfig: { localEndTurnCount, localWarningThreshold, localAskInterval, sessionIdleTimeoutSec } });
    } catch (e) {
      log({ error: 'Failed to load local ending config', message: e.message });
    }
  }

  // 로컬 엔딩 UI 업데이트
  function updateLocalEndingUI(turnCount) {
    const remaining = localEndTurnCount - turnCount;

    // 턴 카운트 배지
    document.getElementById('talkTurnBadge').textContent = `Turn: ${turnCount}/${localEndTurnCount}`;

    // 남은 턴 배지 (색상 변경)
    const remainingBadge = document.getElementById('talkRemainingBadge');
    remainingBadge.textContent = `남은 턴: ${remaining}`;
    if (remaining <= 0) {
      remainingBadge.style.background = '#ef4444'; // red
    } else if (remaining <= localWarningThreshold) {
      remainingBadge.style.background = '#f59e0b'; // orange
    } else {
      remainingBadge.style.background = '#10b981'; // green
    }

    // 종료 임박 배지
    const warningBadge = document.getElementById('talkLocalWarningBadge');
    if (remaining <= localWarningThreshold && remaining > 0) {
      warningBadge.style.display = 'inline-block';
    } else {
      warningBadge.style.display = 'none';
    }

    // N턴마다 질문 배지
    const askBadge = document.getElementById('talkAskContinueBadge');
    if (turnCount > 0 && turnCount % localAskInterval === 0) {
      askBadge.style.display = 'inline-block';
    } else {
      askBadge.style.display = 'none';
    }
  }

  // 세션 타임아웃 타이머
  let sessionTimeoutIntervalId = null;

  function clearSessionTimeout() {
    if (sessionTimeoutTimerId) {
      clearTimeout(sessionTimeoutTimerId);
      sessionTimeoutTimerId = null;
    }
    if (sessionTimeoutIntervalId) {
      clearInterval(sessionTimeoutIntervalId);
      sessionTimeoutIntervalId = null;
    }
  }

  function startSessionTimeout() {
    clearSessionTimeout();
    sessionTimeoutRemaining = sessionIdleTimeoutSec;
    updateTimeoutDisplay();

    // 1초마다 카운트다운
    sessionTimeoutIntervalId = setInterval(() => {
      sessionTimeoutRemaining--;
      updateTimeoutDisplay();
      if (sessionTimeoutRemaining <= 0) {
        clearSessionTimeout();
        toast('세션 타임아웃 - 대화 종료', 'error');
        endTalk();
      }
    }, 1000);
  }

  function updateTimeoutDisplay() {
    const min = Math.floor(sessionTimeoutRemaining / 60);
    const sec = sessionTimeoutRemaining % 60;
    const display = `${min}:${sec.toString().padStart(2, '0')}`;
    document.getElementById('talkTimeoutBadge').textContent = `타임아웃: ${display}`;

    // 30초 이하면 빨간색
    const badge = document.getElementById('talkTimeoutBadge');
    if (sessionTimeoutRemaining <= 30) {
      badge.style.background = '#ef4444';
    } else if (sessionTimeoutRemaining <= 60) {
      badge.style.background = '#f59e0b';
    } else {
      badge.style.background = '#6b7280';
    }
  }

  function addChatMessage(role, text) {
    const el = document.createElement('div');
    el.className = 'message ' + role;
    el.style.cssText = 'padding: 8px 12px; margin: 8px 0; border-radius: 8px; ' +
      (role === 'user' ? 'background: var(--primary); color: white; margin-left: 20%;' :
       role === 'assistant' ? 'background: white; border: 1px solid var(--border); margin-right: 20%;' :
       'background: var(--muted); color: white; text-align: center; font-size: 12px;');
    el.textContent = text;
    document.getElementById('chatMessages').appendChild(el);
    el.scrollIntoView({ behavior: 'smooth' });
    return el;
  }

  async function startTalk() {
    if (!currentIdleId) {
      toast('먼저 Formation에서 Idle Random을 실행하세요', 'error');
      return;
    }

    showSpinner(true);

    // 로컬 엔딩 config 로드
    await loadLocalEndingConfig();

    const model = document.getElementById('talkModel').value;

    // 세션이 없으면 자동 생성 (대화기용 - 닉네임 기본값 사용)
    if (!sessionId) {
      try {
        const sessData = await fetchJson('/session/start', {
          method: 'POST',
          body: JSON.stringify({})
        });
        sessionId = sessData.session_id;
        document.getElementById('sessionId').textContent = sessionId;
        log({ endpoint: '/session/start (auto)', data: sessData });
      } catch (e) {
        showSpinner(false);
        toast(`Session auto-create failed: ${e.message}`, 'error');
        return;
      }
    }

    try {
      const data = await fetchJson('/talk/start', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          idle_id: currentIdleId,
          model: model
        })
      });

      // 채팅 영역 표시
      document.getElementById('talkChatArea').style.display = 'block';
      document.getElementById('btnStartTalk').style.display = 'none';
      document.getElementById('chatMessages').innerHTML = '';
      addChatMessage('system', `[혼잣말] ${data.idle_text}`);
      addChatMessage('assistant', data.assistant_first_text);

      // 턴 카운트 초기화
      talkTurnCount = 1;
      updateLocalEndingUI(talkTurnCount);
      document.getElementById('talkPolicyBadge').style.display = 'none';
      document.getElementById('talkStatusText').textContent = '';

      log({ endpoint: '/talk/start', data });
      toast('Talk started', 'success', 2000);

      // auto-nudge 타이머 시작
      nudgeFiredThisTurn = false;
      startNudgeTimer();

      // 세션 타임아웃 시작
      startSessionTimeout();
    } catch (e) {
      toast(`Talk start failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function sendTalk() {
    const input = document.getElementById('talkInput');
    const userText = input.value.trim();
    if (!userText) return;

    if (!sessionId) {
      toast('세션이 없습니다', 'error');
      return;
    }

    // 새 턴 시작 - nudge 플래그 리셋
    nudgeFiredThisTurn = false;

    input.value = '';
    addChatMessage('user', userText);
    showSpinner(true);

    const model = document.getElementById('talkModel').value;

    try {
      const data = await fetchJson('/talk/turn', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          user_text: userText,
          model: model
        })
      });

      addChatMessage('assistant', data.ui_text);
      log({ endpoint: '/talk/turn', data });

      // 턴 카운트 증가 & 로컬 엔딩 UI 업데이트
      talkTurnCount++;
      updateLocalEndingUI(talkTurnCount);

      // 정책 가이드 표시
      if (data.policy_category) {
        document.getElementById('talkPolicyBadge').style.display = 'inline-block';
        document.getElementById('talkPolicyBadge').textContent = `정책: ${data.policy_category}`;
        document.getElementById('talkStatusText').textContent = '정책 가이드가 LLM에 주입됨';
      } else {
        document.getElementById('talkPolicyBadge').style.display = 'none';
        document.getElementById('talkStatusText').textContent = '';
      }

      // 글로벌 예고 표시
      if (data.warning_text) {
        document.getElementById('globalWarningBox').style.display = 'block';
        document.getElementById('globalWarningText').textContent = data.warning_text;
      }

      // 글로벌 엔딩
      if (data.global_ended) {
        addChatMessage('system', '🔴 사노의 시간이 모두 끝났습니다.');
        document.getElementById('talkInput').disabled = true;
        clearNudgeTimer();
        clearSessionTimeout();
        toast('글로벌 엔딩 - 사노 종료', 'error');
      } else if (data.should_end) {
        addChatMessage('system', '🟡 로컬 엔딩 - 세션 토큰 소진');
        clearNudgeTimer();
        clearSessionTimeout();
        toast('로컬 엔딩 - 대화 종료', 'info');
      } else {
        // 대화 계속 - 타이머 리셋
        startNudgeTimer();
        startSessionTimeout();
      }
    } catch (e) {
      toast(`Talk turn failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function sendNudge() {
    if (!sessionId) {
      toast('세션이 없습니다', 'error');
      return;
    }
    if (!currentIdleId) {
      toast('대화가 시작되지 않았습니다', 'error');
      return;
    }

    showSpinner(true);
    const model = document.getElementById('talkModel').value;

    try {
      const data = await fetchJson('/monologue/nudge', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          model: model
        })
      });

      addChatMessage('system', '[nudge]');
      addChatMessage('assistant', data.nudge_text);
      log({ endpoint: '/monologue/nudge', data });
      // 수동 nudge 후 타이머 리셋
      startNudgeTimer();
      startSessionTimeout();
    } catch (e) {
      toast(`Nudge failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  function endTalk() {
    // 타이머 정리
    clearNudgeTimer();
    clearSessionTimeout();
    nudgeFiredThisTurn = false;

    document.getElementById('talkChatArea').style.display = 'none';
    document.getElementById('btnStartTalk').style.display = 'inline-block';
    document.getElementById('chatMessages').innerHTML = '<div class="message system">대화가 시작되면 여기에 표시됩니다</div>';
    currentIdleId = null;
    currentIdleText = null;
    talkTurnCount = 0;
    document.getElementById('selectedIdleText').textContent = '혼잣말을 선택하세요 (Formation → Idle Random)';

    // 로컬 엔딩 UI 리셋
    document.getElementById('talkTurnBadge').textContent = 'Turn: 0/50';
    document.getElementById('talkRemainingBadge').textContent = '남은 턴: 50';
    document.getElementById('talkRemainingBadge').style.background = '#10b981';
    document.getElementById('talkLocalWarningBadge').style.display = 'none';
    document.getElementById('talkAskContinueBadge').style.display = 'none';
    document.getElementById('talkPolicyBadge').style.display = 'none';
    document.getElementById('talkTimeoutBadge').textContent = '타임아웃: --:--';
    document.getElementById('talkTimeoutBadge').style.background = '#6b7280';
    document.getElementById('talkStatusText').textContent = '';
    document.getElementById('globalWarningBox').style.display = 'none';
    document.getElementById('talkInput').disabled = false;

    toast('Talk ended', 'success', 2000);
  }

  // Admin
  async function fetchAdminProgress() {
    try {
      const data = await fetchJson('/admin/progress');
      document.getElementById('admAnswered').textContent = data.answered_count ?? '-';
      document.getElementById('admMax').textContent = data.max_questions ?? '-';
      document.getElementById('admRatio').textContent = Math.round((data.progress_ratio || 0) * 100) + '%';
      document.getElementById('admPhase').textContent = data.phase ?? '-';
      document.getElementById('admGlobalTurn').textContent = `${data.global_turn_count ?? 0}/${data.global_turn_max ?? 365}`;
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

  async function adminImportIdle() {
    const file = document.getElementById('admIdleXlsxFile').files[0];
    if (!file) return log('No file selected');
    const fd = new FormData();
    fd.append('file', file);
    try {
      const data = await fetchMultipart('/admin/idle/import', fd);
      log({ endpoint: '/admin/idle/import', data });
      toast(`Idle import: ${data.inserted} inserted, ${data.updated} updated`, 'success');
    } catch (e) {
      log({ error: e.message });
      toast(`Idle import failed: ${e.message}`, 'error');
    }
  }

  async function adminImportPolicyRules() {
    const file = document.getElementById('admPolicyRulesXlsxFile').files[0];
    if (!file) return log('No file selected');
    const fd = new FormData();
    fd.append('file', file);
    try {
      const data = await fetchMultipart('/admin/policy-rules/import', fd);
      log({ endpoint: '/admin/policy-rules/import', data });
      toast(`Policy Rules import: ${data.inserted} inserted, ${data.updated} updated`, 'success');
      // Policy Rules 목록 새로고침
      if (typeof loadPolicyRules === 'function') loadPolicyRules();
    } catch (e) {
      log({ error: e.message });
      toast(`Policy Rules import failed: ${e.message}`, 'error');
    }
  }

  async function personaGenerate() {
    const body = {};
    if (document.getElementById('personaForce').checked) body.force = true;

    showSpinner(true);
    toast('페르소나 생성 중...', 'info', 3000);
    try {
      const data = await fetchJson('/persona/generate', { method: 'POST', body: JSON.stringify(body) });
      log({ endpoint: '/persona/generate', data });

      if (data.reused) {
        toast('기존 persona 재사용됨 (force로 재생성 가능)', 'info');
      } else {
        toast('페르소나 생성 완료', 'success');
      }
      await refreshState();
    } catch (e) {
      toast(`페르소나 생성 실패: ${e.message}`, 'error');
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
          <th style="padding: 8px 4px;">Description</th>
          <th style="padding: 8px 4px; width: 60px;">Action</th>
        </tr>
      </thead>
      <tbody>`;

    for (const c of configsCache) {
      const inputType = (c.type === 'int' || c.type === 'float') ? 'number' : 'text';
      const step = c.type === 'float' ? 'step="0.01"' : '';
      html += `<tr style="border-bottom: 1px solid var(--border);">
        <td style="padding: 6px 4px; font-family: var(--mono); font-size: 11px;">${c.key}</td>
        <td style="padding: 6px 4px;">
          <input type="${inputType}" ${step} id="cfg_${c.key}" value="${escapeHtml(c.value)}" style="width: 100%; font-size: 11px;" />
        </td>
        <td style="padding: 6px 4px; color: var(--muted);">${c.type}</td>
        <td style="padding: 6px 4px; font-size: 10px; color: var(--muted);">${escapeHtml(c.description || '-')}</td>
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

  // Policy Rules
  async function loadPolicyRules() {
    const enabledOnly = document.getElementById('policyEnabledOnly').checked;

    showSpinner(true);
    try {
      const data = await fetchJson(`/admin/policy-rules?enabled_only=${enabledOnly}`);

      const box = document.getElementById('policyRulesBox');
      if (!data.items || data.items.length === 0) {
        box.innerHTML = '<div style="color: var(--muted);">No policy rules found</div>';
        showSpinner(false);
        return;
      }

      let html = `<div style="margin-bottom: 8px; font-size: 12px; color: var(--muted);">Total: ${data.total}</div>`;
      html += `<table style="width: 100%; font-size: 11px;"><thead><tr>
        <th style="padding: 6px;">ID</th>
        <th style="padding: 6px;">Category</th>
        <th style="padding: 6px;">Keywords</th>
        <th style="padding: 6px;">Action</th>
        <th style="padding: 6px;">Pri</th>
        <th style="padding: 6px;">Enabled</th>
      </tr></thead><tbody>`;

      for (const r of data.items) {
        const keywordsShort = r.keywords.length > 30 ? r.keywords.substring(0, 30) + '...' : r.keywords;
        const actionBadge = r.action === 'block' ? 'badge-danger' : r.action === 'crisis' ? 'badge-warning' : '';
        html += `<tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 6px; font-family: var(--mono);">${r.id}</td>
          <td style="padding: 6px;">${escapeHtml(r.category)}</td>
          <td style="padding: 6px; font-size: 10px; color: var(--muted); max-width: 150px;" title="${escapeHtml(r.keywords)}">${escapeHtml(keywordsShort)}</td>
          <td style="padding: 6px;"><span class="badge ${actionBadge}">${r.action}</span></td>
          <td style="padding: 6px; font-family: var(--mono);">${r.priority}</td>
          <td style="padding: 6px;">
            <button class="btn btn-sm ${r.enabled ? 'btn-primary' : 'btn-ghost'}" onclick="togglePolicyRule(${r.id})">${r.enabled ? 'ON' : 'OFF'}</button>
          </td>
        </tr>`;
      }
      html += '</tbody></table>';
      box.innerHTML = html;

      log({ endpoint: '/admin/policy-rules', total: data.total });
      toast('Policy rules loaded', 'success', 2000);
    } catch (e) {
      toast(`Load policy rules failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function togglePolicyRule(id) {
    try {
      const data = await fetchJson(`/admin/policy-rules/${id}/toggle`, { method: 'PUT' });
      toast(`Policy rule ${id} ${data.enabled ? 'enabled' : 'disabled'}`, 'success', 2000);
      await loadPolicyRules();
    } catch (e) {
      toast(`Toggle failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
  }

  // Idle List
  async function loadIdleList() {
    const limit = document.getElementById('idleLimit').value || 30;
    const offset = document.getElementById('idleOffset').value || 0;
    const enabledOnly = document.getElementById('idleEnabledOnly').checked;

    showSpinner(true);
    try {
      const data = await fetchJson(`/admin/idle/list?limit=${limit}&offset=${offset}&enabled_only=${enabledOnly}`);

      const box = document.getElementById('idleListBox');
      if (!data.items || data.items.length === 0) {
        box.innerHTML = '<div style="color: var(--muted);">No idle items found</div>';
        showSpinner(false);
        return;
      }

      let html = `<div style="margin-bottom: 8px; font-size: 12px; color: var(--muted);">Total: ${data.total}</div>`;
      html += `<table style="width: 100%; font-size: 11px;"><thead><tr>
        <th style="padding: 6px;">ID</th>
        <th style="padding: 6px;">Axis</th>
        <th style="padding: 6px;">Text</th>
        <th style="padding: 6px;">Enabled</th>
      </tr></thead><tbody>`;

      for (const item of data.items) {
        const textShort = item.question_text.length > 50 ? item.question_text.substring(0, 50) + '...' : item.question_text;
        html += `<tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 6px; font-family: var(--mono);">${item.id}</td>
          <td style="padding: 6px; font-size: 10px;">${escapeHtml(item.axis_key)}</td>
          <td style="padding: 6px; font-size: 10px; max-width: 250px;" title="${escapeHtml(item.question_text)}">${escapeHtml(textShort)}</td>
          <td style="padding: 6px;">
            <button class="btn btn-sm ${item.enable ? 'btn-primary' : 'btn-ghost'}" onclick="toggleIdle(${item.id})">${item.enable ? 'ON' : 'OFF'}</button>
          </td>
        </tr>`;
      }
      html += '</tbody></table>';
      box.innerHTML = html;

      log({ endpoint: '/admin/idle/list', total: data.total, shown: data.items.length });
      toast('Idle list loaded', 'success', 2000);
    } catch (e) {
      toast(`Load idle list failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function toggleIdle(id) {
    try {
      const data = await fetchJson(`/admin/idle/${id}/toggle`, { method: 'PUT' });
      toast(`Idle ${id} ${data.enable ? 'enabled' : 'disabled'}`, 'success', 2000);
      await loadIdleList();
    } catch (e) {
      toast(`Toggle failed: ${e.message}`, 'error');
      log({ error: e.message });
    }
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
          <li><strong>Talk</strong> → 365문항 완료 후 대화 가능</li>
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
          <li><strong>Idle Random</strong>: DB에서 가치축별 혼잣말 랜덤 선택 (Talk에서 사용)</li>
          <li><strong>Nudge</strong>: 대화 중 사용자 반응이 없을 때 던지는 한마디 (Talk 세션 필요)</li>
        </ul>
        <p style="color: var(--muted); font-size: 12px;">* 성장단계는 총 답변 수(answered_total)에 따라 1~6단계로 나뉩니다.</p>
      </div>
    `,
    talk: `
      <div class="help-section">
        <h4>💬 Talk (대화)</h4>
        <p>사노의 혼잣말을 바탕으로 자유 대화를 나눌 수 있습니다.</p>
        <ul>
          <li><strong>혼잣말 선택</strong>: Formation → Idle Random으로 혼잣말을 먼저 생성하세요</li>
          <li><strong>Auto-Nudge</strong>: 15초간 입력이 없으면 자동으로 사노가 먼저 말을 겁니다</li>
          <li><strong>Model 선택</strong>: 대화에 사용할 LLM 모델 선택
            <ul style="margin-top:4px; font-size:12px; color:var(--muted);">
              <li>gpt-4o-mini: 빠름, 저렴</li>
              <li>gpt-4o: 균형</li>
              <li>gpt-5-mini: GPT-5 경량</li>
              <li>gpt-5.2: 최신 flagship</li>
            </ul>
          </li>
          <li><strong>대화 시작</strong>: 선택한 혼잣말과 모델로 대화 시작</li>
          <li><strong>End Talk</strong>: 대화 종료</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>⚠️ 주의사항</h4>
        <ul>
          <li>혼잣말을 먼저 선택해야 대화를 시작할 수 있습니다</li>
          <li>정책 규칙(자해/개인정보 등)에 의해 응답이 필터링될 수 있음</li>
          <li>선택한 모델은 대화 시작과 턴마다 적용됩니다</li>
        </ul>
      </div>
    `,
    admin: `
      <div class="help-section">
        <h4>⚙️ Admin (관리)</h4>
        <p>시스템 상태 확인 및 제어 기능입니다.</p>
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
        <p>365문항 완료 후 LLM으로 사노의 persona_prompt 생성</p>
        <ul>
          <li><strong>force</strong>: 기존 persona가 있어도 재생성</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>⚡ Quick Test</h4>
        <p>빠른 테스트를 위한 자동화 기능</p>
        <ul>
          <li>세션 생성 → 지정 개수만큼 랜덤 답변 → 세션 종료</li>
        </ul>
      </div>
    `,
    data: `
      <div class="help-section">
        <h4>📊 Data (데이터 관리)</h4>
        <p>사노의 콘텐츠 데이터를 확인하고 관리합니다.</p>
      </div>
      <div class="help-section">
        <h4>📋 Questions</h4>
        <p>A/B 질문 목록 확인 및 활성화/비활성화 토글</p>
      </div>
      <div class="help-section">
        <h4>💬 Idle List</h4>
        <p>혼잣말 목록 확인 및 활성화/비활성화 토글</p>
      </div>
      <div class="help-section">
        <h4>🛡️ Policy Rules</h4>
        <p>정책 필터 규칙 확인 및 활성화/비활성화 토글</p>
        <ul>
          <li>민감 주제(자해, 개인정보 등) 감지 키워드</li>
          <li>action: redirect, block, crisis, privacy</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>🌱 Growth Stages</h4>
        <p>사노의 성장 단계별 설정 확인 (6단계)</p>
      </div>
      <div class="help-section">
        <h4>📁 Recent Sessions</h4>
        <p>최근 세션 기록 조회</p>
      </div>
    `,
    settings: `
      <div class="help-section">
        <h4>🔧 Settings (설정)</h4>
        <p>시스템 설정 및 프롬프트 템플릿을 관리합니다.</p>
      </div>
      <div class="help-section">
        <h4>⚙️ Config Settings</h4>
        <p>DB에 저장된 설정값 조회 및 수정</p>
        <ul>
          <li>임계값, 최대값, 모델 설정 등</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>📝 Prompt Templates</h4>
        <p>LLM 프롬프트 템플릿 관리</p>
        <ul>
          <li>변수 클릭으로 삽입</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>📥 Import</h4>
        <p>xlsx 파일로 데이터 일괄 업로드</p>
        <ul>
          <li>Questions, Settings, Idle</li>
        </ul>
      </div>
      <div class="help-section">
        <h4>🎯 Personality Values</h4>
        <p>사노의 성격 값 직접 조회/수정</p>
      </div>
      <div class="help-section">
        <h4>🎭 Current Persona</h4>
        <p>현재 저장된 페르소나 프롬프트 확인</p>
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
  fetchAdminProgress();
</script>

</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
def ui():
    return HTMLResponse(content=HTML)
