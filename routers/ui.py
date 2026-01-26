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
  </style>
</head>

<body>
  <div class="app">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div>
        <div class="logo">Psano</div>
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
                <label class="form-label">Model (optional)</label>
                <input type="text" id="personaModel" placeholder="gpt-4o-mini" />
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
      await refreshState();
    } catch (e) {
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function endSession() {
    if (!sessionId) return log('No session');
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
    } catch (e) {
      log({ error: e.message });
    }
    showSpinner(false);
  }

  // Question
  async function getCurrentQuestion() {
    if (!sessionId) return log('No session');
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
      log({ error: e.message });
    }
    showSpinner(false);
  }

  async function sendAnswer(choice) {
    if (!sessionId || !lastQuestionId) return log('No session or question');
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
        log('Session completed! Click End to finish.');
      }
      await refreshState();
    } catch (e) {
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
    if (!sessionId) return log('No session');
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
    } catch (e) {
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
      log({ error: e.message });
    }
  }

  async function talkEnd() {
    if (!sessionId) return log('No session');
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
    } catch (e) {
      log({ error: e.message });
    }
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
    const model = document.getElementById('personaModel').value.trim();
    const maxTokens = document.getElementById('personaMaxTokens').value;
    if (model) body.model = model;
    if (maxTokens) body.max_output_tokens = parseInt(maxTokens);
    if (document.getElementById('personaForce').checked) body.force = true;

    showSpinner(true);
    try {
      const data = await fetchJson('/persona/generate', { method: 'POST', body: JSON.stringify(body) });
      log({ endpoint: '/persona/generate', data });
      await refreshState();
    } catch (e) {
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