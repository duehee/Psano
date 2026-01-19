from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

HTML = r"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Psano MVP Console</title>
  <style>
    :root {
      --bg: #0b1220;
      --panel: rgba(255,255,255,0.06);
      --panel2: rgba(255,255,255,0.09);
      --text: rgba(255,255,255,0.92);
      --muted: rgba(255,255,255,0.60);
      --line: rgba(255,255,255,0.10);
      --good: #2dd4bf;
      --warn: #fbbf24;
      --bad:  #fb7185;
      --btn: rgba(255,255,255,0.10);
      --btn2: rgba(255,255,255,0.16);
      --shadow: 0 14px 50px rgba(0,0,0,0.35);
      --radius: 18px;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      color: var(--text);
      background: radial-gradient(1200px 800px at 15% 10%, rgba(45,212,191,0.12), transparent 60%),
                  radial-gradient(1200px 800px at 85% 20%, rgba(251,113,133,0.10), transparent 60%),
                  var(--bg);
      min-height: 100vh;
      padding: 28px;
    }
    .wrap { max-width: 1050px; margin: 0 auto; }
    header {
      display:flex; align-items:flex-end; justify-content:space-between;
      gap: 16px; margin-bottom: 18px;
    }
    h1 { margin: 0; font-size: 22px; letter-spacing: 0.2px; }
    .sub { color: var(--muted); font-size: 13px; margin-top: 6px; }
    .pill {
      font-family: var(--mono);
      font-size: 12px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.04);
      border-radius: 999px;
      color: var(--muted);
      display:inline-flex; align-items:center; gap: 8px;
    }
    .dot { width: 8px; height: 8px; border-radius: 99px; background: var(--warn); }
    .grid {
      display:grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 16px;
    }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .card .hd {
      padding: 14px 16px;
      display:flex; align-items:center; justify-content:space-between; gap: 10px;
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,0.03);
    }
    .title { font-size: 14px; color: rgba(255,255,255,0.82); }
    .body { padding: 14px 16px; }
    .row { display:flex; gap: 10px; flex-wrap: wrap; align-items:center; }
    button {
      cursor:pointer;
      border: 1px solid var(--line);
      background: var(--btn);
      color: var(--text);
      padding: 9px 12px;
      border-radius: 12px;
      font-size: 13px;
      transition: transform .04s ease, background .12s ease;
    }
    button:hover { background: var(--btn2); }
    button:active { transform: translateY(1px); }
    button.primary { border-color: rgba(45,212,191,0.35); background: rgba(45,212,191,0.14); }
    button.danger { border-color: rgba(251,113,133,0.35); background: rgba(251,113,133,0.12); }
    button.ghost { background: transparent; }
    .kbd {
      font-family: var(--mono);
      font-size: 12px;
      padding: 6px 8px;
      border: 1px solid var(--line);
      border-radius: 10px;
      color: var(--muted);
      background: rgba(0,0,0,0.18);
    }
    input, textarea {
      width: 100%;
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.22);
      color: var(--text);
      outline: none;
      font-size: 13px;
    }
    textarea { min-height: 100px; resize: vertical; }
    input[type="file"] { width: auto; padding: 8px 10px; }
    select {
      padding: 10px 12px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.22);
      color: var(--text);
      outline: none;
      font-size: 13px;
    }

    .mono { font-family: var(--mono); }
    .muted { color: var(--muted); }
    .sep { height: 1px; background: var(--line); margin: 12px 0; }
    .badge {
      font-family: var(--mono);
      font-size: 12px;
      border: 1px solid var(--line);
      padding: 6px 8px;
      border-radius: 10px;
      background: rgba(255,255,255,0.04);
      color: var(--muted);
      max-width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .out {
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.20);
      border-radius: 14px;
      padding: 12px;
      white-space: pre-wrap;
      line-height: 1.45;
    }
    .small { font-size: 12px; }
    .status-ok .dot { background: var(--good); }
    .status-warn .dot { background: var(--warn); }
    .status-bad .dot { background: var(--bad); }
    .two { display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .spin {
      width: 14px; height: 14px; border-radius: 999px;
      border: 2px solid rgba(255,255,255,0.25);
      border-top-color: rgba(255,255,255,0.85);
      animation: rot .8s linear infinite;
      display:none;
    }
    @keyframes rot { to { transform: rotate(360deg); } }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      border-bottom: 1px solid rgba(255,255,255,0.10);
      padding: 8px 6px;
      vertical-align: top;
    }
    th { color: rgba(255,255,255,0.75); font-weight: 600; text-align: left; }
    td { color: rgba(255,255,255,0.82); }
    .right { text-align:right; }

    .chk {
      display:inline-flex;
      gap:6px;
      align-items:center;
      font-size:12px;
      color: rgba(255,255,255,0.75);
      user-select:none;
    }
    .chk input { width:auto; }

    .hint {
      font-size: 12px;
      color: rgba(255,255,255,0.62);
      line-height: 1.4;
      margin-top: 8px;
    }

    /* ===== Talk chat UI (NEW) ===== */
    .chatWrap {
      border: 1px solid var(--line);
      background: rgba(0,0,0,0.18);
      border-radius: 16px;
      padding: 12px;
    }

    .chatList {
      height: 360px;
      overflow: auto;
      padding: 6px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .bubbleRow {
      display: flex;
      align-items: flex-end;
      gap: 8px;
    }
    .bubbleRow.user { justify-content: flex-end; }
    .bubbleRow.assistant { justify-content: flex-start; }
    .bubbleRow.system { justify-content: center; }

    .bubble {
      max-width: 78%;
      padding: 10px 12px;
      border-radius: 16px;
      line-height: 1.45;
      font-size: 13px;
      border: 1px solid rgba(255,255,255,0.10);
      white-space: pre-wrap;
      word-break: break-word;
    }

    .bubble.user {
      background: rgba(45,212,191,0.14);
      border-color: rgba(45,212,191,0.28);
    }

    .bubble.assistant {
      background: rgba(255,255,255,0.06);
    }

    .bubble.system {
      background: rgba(255,255,255,0.04);
      color: rgba(255,255,255,0.70);
      border-style: dashed;
      font-size: 12px;
      max-width: 92%;
      text-align: center;
    }

    .chatMeta {
      font-family: var(--mono);
      font-size: 11px;
      color: rgba(255,255,255,0.50);
      margin: 0 4px;
    }

    .chatInputBar {
      margin-top: 12px;
      display: flex;
      gap: 10px;
      align-items: flex-end;
    }

    .chatInputBar textarea {
      min-height: 56px;
      resize: none;
    }

    /* ===== Chat mode (focus) ===== */
    body.mode-chat .grid { grid-template-columns: 1fr; }
    body.mode-chat #debugCard { display: none; }
    body.mode-chat #formationCard { display: none; }
    body.mode-chat #adminCard { display: none; }
    body.mode-chat .chatList { height: 520px; }
  </style>
</head>

<body>
  <div class="wrap">
    <header>
      <div>
        <h1>Psano MVP Console</h1>
        <div class="sub">버튼으로 바로 굴리는 로컬 UI / HTTP only</div>
      </div>
      <div id="healthPill" class="pill status-warn" title="서버 상태">
        <span class="dot"></span>
        <span class="mono">health: unknown</span>
        <span id="spinner" class="spin"></span>
      </div>
    </header>

    <div class="grid">
      <!-- Left: main flow -->
      <section class="card">
        <div class="hd">
          <div class="title">Session / Formation / Talk</div>
          <div class="row">
            <span id="sessionBadge" class="badge mono">session_id: -</span>
            <button class="primary" onclick="startSession()">Start</button>
            <button class="danger" onclick="endSession()">End</button>
          </div>
        </div>

        <div class="body">
          <div class="row">
            <button onclick="checkHealth()">Health</button>
            <button onclick="refreshState()">State</button>
            <span class="kbd">Tip: Start(이름) → Question → Answer 반복 → talk 되면 Talk</span>
          </div>

          <div class="sep"></div>

          <div class="card" style="box-shadow:none; background: var(--panel2);">
            <div class="hd">
              <div class="title">Session Start</div>
            </div>
            <div class="body">
              <div class="row" style="width:100%">
                <div style="flex:1; min-width:240px">
                  <input id="visitorName" placeholder="방문자 이름(닉네임 가능) 입력..." maxlength="100" />
                </div>
              </div>
              <div class="sub" style="margin-top:10px">
                Start는 <span class="mono">POST /session/start</span>로 <span class="mono">visitor_name</span>을 먼저 입력해 주세요.
              </div>
            </div>
          </div>

          <div class="sep"></div>

          <div id="formationCard" class="card" style="box-shadow:none; background: var(--panel2);">
            <div class="hd">
              <div class="title">Formation (A/B)</div>
              <div class="row">
                <button onclick="getCurrentQuestion()">Get current question</button>
                <span id="qBadge" class="badge mono">question_id: -</span>
              </div>
            </div>
            <div class="body">
              <div id="questionBox" class="out muted small">아직 질문 없음</div>
              <div class="sep"></div>
              <div class="two">
                <button class="primary" onclick="sendAnswer('A')">Choose A</button>
                <button onclick="sendAnswer('B')">Choose B</button>
              </div>
              <div class="sub" style="margin-top:10px">
                <span class="mono">GET /question/current</span>로 받고, <span class="mono">POST /answer</span>로 저장합니다.
              </div>
            </div>
          </div>

          <div class="sep"></div>

          <!-- Talk card (Chat UI) -->
          <div id="talkCard" class="card" style="box-shadow:none; background: var(--panel2);">
            <div class="hd">
              <div class="title">Talk (채팅)</div>
              <div class="row">
                <button onclick="loadTopics()">Load topics</button>
                <button class="ghost" onclick="toggleChatMode()">대화 모드</button>
                <button class="ghost" onclick="clearChatUI()">Clear</button>
                <button class="ghost" onclick="setExample()">Example</button>
                <button class="danger" onclick="talkEnd()">Talk End</button>    
              </div>
            </div>

            <div class="body">
              <div class="row" style="width:100%">
                <select id="topicSelect" style="min-width: 220px;">
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4</option>
                  <option value="5">5</option>
                  <option value="6">6</option>
                  <option value="7">7</option>
                  <option value="8">8</option>
                  <option value="9">9</option>
                  <option value="10">10</option>
                </select>
                <span id="topicBadge" class="badge mono">topic_id: -</span>
              </div>

              <div class="hint" id="topicHint">
                topics를 로드하면 title/description이 표시됩니다. Talk Start는 <span class="mono">POST /talk/start</span> 호출입니다.
              </div>

              <div class="sep"></div>

              <div class="chatWrap">
                <div id="chatList" class="chatList">
                  <div class="bubbleRow system">
                    <div class="bubble system">아직 대화가 없습니다. Talk Start를 눌러 시작해 주세요.</div>
                  </div>
                </div>

                <div class="chatInputBar">
                  <textarea id="talkInput" placeholder="메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"></textarea>
                  <div style="display:flex; flex-direction:column; gap:10px; min-width: 130px;">
                    <button class="primary" onclick="talkStart()">Talk Start</button>
                    <button class="primary" onclick="sendTalk()">Send</button>
                  </div>
                </div>
              </div>

              <!-- 기존 Debug용 출력(호환 유지) -->
              <div id="talkOutput" class="out muted small" style="display:none">아직 응답 없음</div>

              <div class="sub" style="margin-top:10px">
                teach 단계면 Talk은 사용할 수 없는 것이 정상입니다(409).
              </div>
            </div>
          </div>

          <div class="sep"></div>

          <!-- Admin panel -->
          <div id="adminCard" class="card" style="box-shadow:none; background: var(--panel2);">
            <div class="hd">
              <div class="title">Admin</div>
              <div class="row">
                <button onclick="fetchAdminProgress()">Progress</button>
                <button onclick="fetchAdminSessions()">Sessions</button>
                <button class="ghost" onclick="refreshAdminAll()">Refresh all</button>
              </div>
            </div>
            <div class="body">
              <div class="row">
                <div class="badge mono">answered: <span id="admAnswered">-</span>/<span id="admMax">-</span></div>
                <div class="badge mono">ratio: <span id="admRatio">-</span></div>
                <div class="badge mono">phase: <span id="admPhase">-</span></div>
                <div class="badge mono">current_q: <span id="admCurrentQ">-</span></div>
              </div>

              <div class="sep"></div>

              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Reset</div>
                  <div class="sub">POST <span class="mono">/admin/reset</span></div>
                </div>
                <div class="row">
                  <label class="chk"><input id="resetAnswers" type="checkbox" /> answers</label>
                  <label class="chk"><input id="resetSessions" type="checkbox" /> sessions</label>
                  <label class="chk"><input id="resetState" type="checkbox" /> state</label>
                  <label class="chk"><input id="resetPsanoPersonality" type="checkbox" /> personality</label>
                  <button class="danger" onclick="adminReset()">Reset</button>
                </div>
              </div>

              <div class="sep"></div>

              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Phase set (test)</div>
                  <div class="sub">POST <span class="mono">/admin/phase/set</span></div>
                </div>
                <div class="row" style="min-width: 240px;">
                  <select id="admPhaseSelect">
                    <option value="teach">teach</option>
                    <option value="talk">talk</option>
                  </select>
                  <button onclick="adminSetPhase()">Apply</button>
                </div>
              </div>

              <div class="sep"></div>

              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Set current_question (test)</div>
                  <div class="sub">POST <span class="mono">/admin/state/set_current_question</span></div>
                </div>
                <div class="row">
                  <input id="admSetQ" value="1" style="width:110px" />
                  <button onclick="adminSetCurrentQuestion()">Apply</button>
                </div>
              </div>

              <div class="sep"></div>

              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Questions import (xlsx)</div>
                  <div class="sub">POST <span class="mono">/admin/questions/import</span></div>
                </div>
                <div class="row" style="width:100%">
                  <input id="admXlsxFile" type="file" accept=".xlsx" />
                  <button class="primary" onclick="adminImportQuestions()">Upload</button>
                </div>
                <div class="hint">
                  엑셀(.xlsx)을 올리면 <span class="mono">questions</span> 테이블이 upsert 됩니다.
                </div>
              </div>

              <div class="sep"></div>

              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Persona generate</div>
                  <div class="sub">POST <span class="mono">/persona/generate</span></div>
                </div>
                <div class="row" style="width:100%">
                  <input id="personaModel" class="mono" placeholder="model (optional)" style="max-width:240px" />
                  <input id="personaMaxTokens" class="mono" placeholder="max_output_tokens (optional)" style="max-width:220px" />
                  <label class="chk"><input id="personaForce" type="checkbox" /> force</label>
                  <button class="primary" onclick="personaGenerate()">Generate</button>
                </div>
                <div class="hint">
                  테스트용입니다. 성공하면 <span class="mono">/state</span>에서 phase 확인이 가능합니다.
                </div>
              </div>

              <div class="sep"></div>

              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">최근 세션</div>
                </div>
                <div class="row">
                  <span class="kbd">limit</span>
                  <input id="admLimit" value="20" style="width:80px" />
                  <span class="kbd">offset</span>
                  <input id="admOffset" value="0" style="width:80px" />
                </div>
              </div>

              <div class="sep"></div>

              <div class="out mono small" id="admSessionsBox">(아직 불러오지 않음)</div>
            </div>
          </div>
          <!-- Admin end -->
        </div>
      </section>

      <!-- Right: debug panel -->
      <aside id="debugCard" class="card">
        <div class="hd">
          <div class="title">Debug</div>
          <div class="row">
            <button onclick="clearLog()">Clear</button>
          </div>
        </div>
        <div class="body">
          <div class="row">
            <div class="badge mono">phase: <span id="phaseVal">-</span></div>
            <div class="badge mono">current_q: <span id="currentQVal">-</span></div>
            <div class="badge mono">formed_at: <span id="formedAtVal">-</span></div>
          </div>
          <div class="sep"></div>
          <div class="out mono small" id="log"></div>
          <div class="sub" style="margin-top:12px">
            현재 UI는 다음 엔드포인트에 맞춰 동작합니다:
            <span class="mono">/session/start</span>,
            <span class="mono">/question/current</span>,
            <span class="mono">/answer</span>,
            <span class="mono">/state</span>,
            <span class="mono">/talk/topics</span>,
            <span class="mono">/talk/start</span>,
            <span class="mono">/talk/turn</span>,
            <span class="mono">/persona/generate</span>,
            <span class="mono">/admin/progress</span>,
            <span class="mono">/admin/sessions</span>,
            <span class="mono">/admin/reset</span>,
            <span class="mono">/admin/phase/set</span>,
            <span class="mono">/admin/state/set_current_question</span>,
            <span class="mono">/admin/questions/import</span>
          </div>
        </div>
      </aside>
    </div>
  </div>

<script>
  let sessionId = null;
  let lastQuestionId = null;

  // talk topic state
  let topicsCache = [];
  let activeTopicId = null;

  const spinner = document.getElementById("spinner");
  const pill = document.getElementById("healthPill");
  const sessionBadge = document.getElementById("sessionBadge");
  const qBadge = document.getElementById("qBadge");
  const questionBox = document.getElementById("questionBox");
  const talkOutput = document.getElementById("talkOutput");
  const logEl = document.getElementById("log");

  // talk topic UI
  const topicSelect = document.getElementById("topicSelect");
  const topicHint = document.getElementById("topicHint");
  const topicBadge = document.getElementById("topicBadge");

  // chat UI
  const chatList = document.getElementById("chatList");

  // admin el
  const admAnswered = document.getElementById("admAnswered");
  const admMax = document.getElementById("admMax");
  const admRatio = document.getElementById("admRatio");
  const admPhase = document.getElementById("admPhase");
  const admCurrentQ = document.getElementById("admCurrentQ");
  const admSessionsBox = document.getElementById("admSessionsBox");

  function setPill(state, text) {
    pill.classList.remove("status-ok", "status-warn", "status-bad");
    pill.classList.add(state);
    pill.querySelector("span.mono").textContent = text;
  }

  function log(obj) {
    const t = new Date().toLocaleTimeString();
    const s = (typeof obj === "string") ? obj : JSON.stringify(obj, null, 2);
    logEl.textContent = `[${t}] ${s}\n\n` + logEl.textContent;
  }

  function logErr(where, e) {
    log({ where, error: e?.message || String(e), data: e?._data || null });
  }

  function clearLog() { logEl.textContent = ""; }
  function startSpin() { spinner.style.display = "inline-block"; }
  function stopSpin() { spinner.style.display = "none"; }

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options
    });
    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; }
    catch { data = { _raw: text }; }

    if (!res.ok) {
      const detail = data?.detail || res.statusText || "request failed";
      const err = new Error(`${res.status} ${detail}`);
      err._data = data;
      throw err;
    }
    return data;
  }

  async function fetchMultipart(url, formData, headers = {}) {
    const res = await fetch(url, {
      method: "POST",
      headers: { ...(headers || {}) },
      body: formData,
    });

    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; }
    catch { data = { _raw: text }; }

    if (!res.ok) {
      const detail = data?.detail || res.statusText || "request failed";
      const err = new Error(`${res.status} ${detail}`);
      err._data = data;
      throw err;
    }
    return data;
  }

  async function checkHealth() {
    startSpin();
    try {
      const data = await fetchJson("/health");
      setPill("status-ok", "health: ok");
      log({ endpoint: "/health", data });
    } catch (e) {
      setPill("status-bad", "health: error");
      logErr("checkHealth", e);
    } finally {
      stopSpin();
    }
  }

  function setExample() {
    document.getElementById("talkInput").value = "사노야, 너는 지금 무엇이 되었어?";
    document.getElementById("talkInput").focus();
  }

  function setSession(id) {
    sessionId = id;
    sessionBadge.textContent = `session_id: ${id || "-"}`;
  }

  function setQuestion(id, text, sessionQuestionIndex = null) {
    lastQuestionId = id;

    if (id == null) {
      qBadge.textContent = "question_id: -";
    } else if (sessionQuestionIndex != null) {
      qBadge.textContent = `question_id: ${id} (${sessionQuestionIndex}/5)`;
    } else {
      qBadge.textContent = `question_id: ${id ?? "-"}`;
    }

    questionBox.textContent = text || "아직 질문 없음";
  }

  function updateStatePanel(st) {
    if (!st) return;
    document.getElementById("phaseVal").textContent = st.phase ?? "-";
    document.getElementById("currentQVal").textContent = st.current_question ?? "-";
    document.getElementById("formedAtVal").textContent = st.formed_at ?? "-";
  }

  async function startSession() {
    const name = document.getElementById("visitorName").value.trim();
    if (!name) return log("visitor_name이 비어 있습니다. 이름을 입력해 주세요.");

    startSpin();
    try {
      const body = { visitor_name: name };
      const data = await fetchJson("/session/start", { method: "POST", body: JSON.stringify(body) });
      setSession(data.session_id);
      log({ endpoint: "/session/start", data });
      await refreshState();

      // 세션 새로 시작하면 토픽/채팅도 초기화
      activeTopicId = null;
      topicBadge.textContent = "topic_id: -";
      clearChatUI();
    } catch (e) {
      logErr("startSession", e);
    } finally {
      stopSpin();
    }
  }

  async function endSession() {
    if (!sessionId) return log("세션이 없습니다. 먼저 Start를 눌러 주세요.");
    startSpin();
    try {
      const body = { session_id: sessionId, reason: "completed" };
      const data = await fetchJson("/session/end", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/session/end", data });
      setSession(null);
      setQuestion(null, "아직 질문 없음");
      activeTopicId = null;
      topicBadge.textContent = "topic_id: -";
      clearChatUI();
      await refreshState();
      await refreshAdminAll();
    } catch (e) {
      logErr("endSession", e);
    } finally {
      stopSpin();
    }
  }

  async function getCurrentQuestion() {
    if (!sessionId) return log("세션이 없습니다. 먼저 Start를 눌러 주세요.");
    startSpin();
    try {
      const data = await fetchJson(`/question/current?session_id=${encodeURIComponent(sessionId)}`);
      const idx = data.session_question_index ?? null;

      let text =
        `[${idx ?? "-"} / 5]\n` +
        `${data.question_text}\n\n` +
        `A) ${data.choice_a}\n` +
        `B) ${data.choice_b}\n\n` +
        `axis_key: ${data.axis_key}`;

      if (data.value_a_key || data.value_b_key) {
        text += `\nvalue_a_key: ${data.value_a_key ?? ""}\nvalue_b_key: ${data.value_b_key ?? ""}`;
      }

      setQuestion(data.id, text, idx);
      log({ endpoint: "/question/current", data });
    } catch (e) {
      logErr("getCurrentQuestion", e);
    } finally {
      stopSpin();
    }
  }

  async function sendAnswer(choice) {
    if (!sessionId) return log("세션이 없습니다. 먼저 Start를 눌러 주세요.");
    if (!lastQuestionId) return log("질문이 없습니다. Get current question을 먼저 눌러 주세요.");

    startSpin();
    try {
      const body = { session_id: sessionId, question_id: lastQuestionId, choice };
      const data = await fetchJson("/answer", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/answer", data });

      if (data.assistant_reaction_text) {
        questionBox.textContent = data.assistant_reaction_text;
      }

      if (data.session_should_end) {
        setQuestion(null, `(형성 완료) ${data.session_question_index ?? 5}/5. 이제 End를 눌러 세션을 종료해 주세요.`);
      } else {
        setQuestion(null, `(저장 완료) ${data.session_question_index ?? "-"}/5. 다음 질문은 Get current question으로 가져와 주세요.`);
      }

      await refreshState();
      await fetchAdminProgress();
    } catch (e) {
      logErr("sendAnswer", e);
    } finally {
      stopSpin();
    }
  }

  // topics load + render
  function _normalizeTopics(raw) {
    if (!raw) return [];
    if (Array.isArray(raw)) return raw;
    if (Array.isArray(raw.topics)) return raw.topics;
    if (Array.isArray(raw.items)) return raw.items;
    return [];
  }

  function renderTopics(topics) {
    const byId = {};
    for (const t of topics) {
      const id = parseInt(t.id, 10);
      if (!isNaN(id)) byId[id] = t;
    }

    topicSelect.innerHTML = "";
    for (let i = 1; i <= 10; i++) {
      const t = byId[i];
      const opt = document.createElement("option");
      opt.value = String(i);
      opt.textContent = t?.title ? `${i}. ${t.title}` : `${i}`;
      topicSelect.appendChild(opt);
    }

    topicsCache = topics;
    updateTopicHint();
  }

  function updateTopicHint() {
    const selectedId = parseInt(topicSelect.value || "0", 10);
    const t = topicsCache.find(x => parseInt(x.id, 10) === selectedId);

    topicBadge.textContent = `topic_id: ${activeTopicId ?? "-"}`;

    if (!t) {
      topicHint.textContent = "topics를 로드하면 title/description이 표시됩니다.";
      return;
    }
    const title = t.title ?? "";
    const desc = t.description ?? "";
    topicHint.textContent = `${selectedId}. ${title} — ${desc}`;
  }

  topicSelect.addEventListener("change", updateTopicHint);

  async function loadTopics() {
    startSpin();
    try {
      const data = await fetchJson("/talk/topics");
      const topics = _normalizeTopics(data);
      renderTopics(topics);
      log({ endpoint: "/talk/topics", data: { count: topics.length } });
    } catch (e) {
      logErr("loadTopics", e);
    } finally {
      stopSpin();
    }
  }

  /* ===== Chat UI helpers ===== */
  function escapeHtml(s) {
    return (s ?? "")
      .toString()
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  function nowTime() {
    try { return new Date().toLocaleTimeString(); }
    catch { return ""; }
  }

  function scrollChatToBottom() {
    if (!chatList) return;
    chatList.scrollTop = chatList.scrollHeight + 9999;
  }

  function appendChat(role, text, meta = "") {
    if (!chatList) return null;

    const row = document.createElement("div");
    row.className = `bubbleRow ${role}`;

    const bubble = document.createElement("div");
    bubble.className = `bubble ${role}`;
    bubble.innerHTML = escapeHtml(text);

    row.appendChild(bubble);

    if (meta && role !== "system") {
      const m = document.createElement("div");
      m.className = "chatMeta";
      m.textContent = meta;
      row.appendChild(m);
    }

    chatList.appendChild(row);
    scrollChatToBottom();
    return bubble;
  }

  function clearChatUI() {
    if (!chatList) return;
    chatList.innerHTML = "";
    appendChat("system", "대화가 초기화되었습니다. Talk Start를 눌러 다시 시작해 주세요.");
  }

  function toggleChatMode() {
    document.body.classList.toggle("mode-chat");
    scrollChatToBottom();
  }

  // talk start
  async function talkStart() {
    if (!sessionId) return log("세션이 없습니다. 먼저 Start를 눌러 주세요.");
    const tid = parseInt(topicSelect.value || "1", 10);

    startSpin();
    try {
      const body = { session_id: sessionId, topic_id: tid };
      const data = await fetchJson("/talk/start", { method: "POST", body: JSON.stringify(body) });

      const first =
        data.assistant_first_text ??
        data.ui_text ??
        data.assistant_text ??
        data.text ??
        "";

      activeTopicId = tid;
      topicBadge.textContent = `topic_id: ${activeTopicId}`;
      updateTopicHint();

      clearChatUI();
      appendChat("system", `대화를 시작합니다. (topic_id: ${tid})`);
      appendChat("assistant", first || "(empty)", nowTime());
      
      const inputEl = document.getElementById("talkInput");
      if (inputEl) inputEl.disabled = false;

      talkOutput.textContent = first || "(empty)";
      log({ endpoint: "/talk/start", data });
      await refreshState();
    } catch (e) {
      logErr("talkStart", e);
      appendChat("system", `시작 실패: ${e?.message || e}`);
    } finally {
      stopSpin();
    }
  }

  // talk turn ( /talk/turn 우선, 없으면 /talk fallback )
  async function sendTalk() {
    if (!sessionId) return log("세션이 없습니다. 먼저 Start를 눌러 주세요.");
    const inputEl = document.getElementById("talkInput");
    const txt = (inputEl?.value || "").trim();
    if (!txt) return log("메시지가 비어 있습니다.");

    const tid = activeTopicId ?? parseInt(topicSelect.value || "1", 10);

    // 유저 말풍선
    appendChat("user", txt, nowTime());
    if (inputEl) inputEl.value = "";
  
    // 타이핑 버블(이 버블을 '최종 응답 버블'로 바꿀 것)
    const typingRow = document.createElement("div");
    typingRow.className = "bubbleRow assistant";

    const typingBubble = document.createElement("div");
    typingBubble.className = "bubble assistant";
    typingBubble.innerHTML = "…";

    const typingMeta = document.createElement("div");
    typingMeta.className = "chatMeta";
    typingMeta.textContent = "typing";

    typingRow.appendChild(typingBubble);
    typingRow.appendChild(typingMeta);
    chatList.appendChild(typingRow);
    scrollChatToBottom();

    startSpin();
    try {
      // 1) /talk/turn 우선
      try {
        const body = { session_id: sessionId, topic_id: tid, user_text: txt };
        const data = await fetchJson("/talk/turn", { method: "POST", body: JSON.stringify(body) });

        const out =
          data.assistant_text ??
          data.ui_text ??
          data.text ??
          "";

        // 타이핑 버블을 최종 응답으로 교체 (추가 append 하지 않음)
        typingBubble.innerHTML = escapeHtml(out || "(empty)");
        typingMeta.textContent = nowTime();

        talkOutput.textContent = out || "(empty)";
        log({ endpoint: "/talk/turn", data });
        await refreshState();
        return;
      } catch (e1) {
        const msg = (e1?.message || "");
        if (!msg.startsWith("404 ")) throw e1;
      }

      // 2) /talk fallback
      const body2 = { session_id: sessionId, user_text: txt };
      const data2 = await fetchJson("/talk", { method: "POST", body: JSON.stringify(body2) });

      const out2 =
        data2.assistant_text ??
        data2.ui_text ??
        data2.text ??
        "";

      typingBubble.innerHTML = escapeHtml(out2 || "(empty)");
      typingMeta.textContent = nowTime();

      talkOutput.textContent = out2 || "(empty)";
      log({ endpoint: "/talk (fallback)", data: data2 });
      await refreshState();
    } catch (e) {
      logErr("sendTalk", e);
      typingBubble.innerHTML = escapeHtml(`에러: ${e?.message || e}`);
      typingMeta.textContent = nowTime();
      appendChat("system", `전송 실패: ${e?.message || e}`);
    } finally {
      stopSpin();
    }
  }
  
  async function talkEnd() {
    if (!sessionId) return log("세션이 없습니다. 먼저 Start를 눌러 주세요.");

    startSpin();
    try {
      const body = { session_id: sessionId };
      const data = await fetchJson("/talk/end", { method: "POST", body: JSON.stringify(body) });

      // 채팅창에 시스템 메시지
      if (typeof appendChat === "function") {
        appendChat("system", `대화가 종료되었습니다. (reason: ${data.end_reason ?? "talk_end"})`);
      } else {
        // 구버전 UI라면 기존 output에 표시
        talkOutput.textContent = "대화가 종료되었습니다.";
      }

      // 입력 비활성화(원하면)
      const inputEl = document.getElementById("talkInput");
      if (inputEl) inputEl.disabled = true;

      // topic 상태 초기화
      activeTopicId = null;
      topicBadge.textContent = "topic_id: -";

      log({ endpoint: "/talk/end", data });
      await refreshState();
      await refreshAdminAll?.();
    } catch (e) {
      logErr("talkEnd", e);
      if (typeof appendChat === "function") {
        appendChat("system", `대화 종료 실패: ${e?.message || e}`);
      }
    } finally {
      stopSpin();
    }
  }



  async function refreshState() {
    startSpin();
    try {
      const data = await fetchJson("/state");
      updateStatePanel(data);
      log({ endpoint: "/state", data });
    } catch (e) {
      logErr("refreshState", e);
    } finally {
      stopSpin();
    }
  }

  // Admin API
  function _pct(x) {
    if (x == null || isNaN(x)) return "-";
    return `${Math.round(x * 1000) / 10}%`;
  }

  async function fetchAdminProgress() {
    startSpin();
    try {
      const data = await fetchJson("/admin/progress");
      admAnswered.textContent = data.answered_count ?? "-";
      admMax.textContent = data.max_questions ?? "-";
      admRatio.textContent = _pct(data.progress_ratio);
      admPhase.textContent = data.phase ?? "-";
      admCurrentQ.textContent = data.current_question ?? "-";
      log({ endpoint: "/admin/progress", data });
    } catch (e) {
      logErr("fetchAdminProgress", e);
    } finally {
      stopSpin();
    }
  }

  function renderSessionsTable(resp) {
    const sessions = resp?.sessions || [];
    if (!sessions.length) return "(세션 없음)";

    let html = "<table>";
    html += "<thead><tr>";
    html += "<th class='right'>id</th>";
    html += "<th>name</th>";
    html += "<th>started</th>";
    html += "<th>ended</th>";
    html += "<th>reason</th>";
    html += "</tr></thead><tbody>";

    for (const s of sessions) {
      html += "<tr>";
      html += `<td class='right'>${s.id ?? ""}</td>`;
      html += `<td>${(s.visitor_name ?? "").toString().replaceAll("<","&lt;")}</td>`;
      html += `<td>${s.started_at ?? ""}</td>`;
      html += `<td>${s.ended_at ?? ""}</td>`;
      html += `<td>${s.end_reason ?? ""}</td>`;
      html += "</tr>";
    }

    html += "</tbody></table>";
    return html;
  }

  async function fetchAdminSessions() {
    startSpin();
    try {
      const limit = parseInt(document.getElementById("admLimit").value || "20", 10);
      const offset = parseInt(document.getElementById("admOffset").value || "0", 10);
      const data = await fetchJson(`/admin/sessions?limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`);
      admSessionsBox.innerHTML = renderSessionsTable(data);
      log({ endpoint: "/admin/sessions", data: { total: data.total, shown: (data.sessions||[]).length } });
    } catch (e) {
      admSessionsBox.textContent = "(불러오기 실패)";
      logErr("fetchAdminSessions", e);
    } finally {
      stopSpin();
    }
  }

  async function refreshAdminAll() {
    await fetchAdminProgress();
    await fetchAdminSessions();
  }

  async function adminReset() {
    startSpin();
    try {
      const body = {
        reset_answers: !!document.getElementById("resetAnswers").checked,
        reset_sessions: !!document.getElementById("resetSessions").checked,
        reset_state: !!document.getElementById("resetState").checked,
        reset_personality: !!document.getElementById("resetPsanoPersonality").checked,
      };
      const data = await fetchJson("/admin/reset", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/admin/reset", data });
      await refreshState();
      await refreshAdminAll();
      setQuestion(null, "아직 질문 없음");
      activeTopicId = null;
      topicBadge.textContent = "topic_id: -";
      clearChatUI();
    } catch (e) {
      logErr("adminReset", e);
    } finally {
      stopSpin();
    }
  }

  async function adminSetPhase() {
    startSpin();
    try {
      const phase = document.getElementById("admPhaseSelect").value;
      const data = await fetchJson("/admin/phase/set", { method: "POST", body: JSON.stringify({ phase }) });
      log({ endpoint: "/admin/phase/set", data });
      await refreshState();
      await refreshAdminAll();
    } catch (e) {
      logErr("adminSetPhase", e);
    } finally {
      stopSpin();
    }
  }

  async function adminSetCurrentQuestion() {
    startSpin();
    try {
      const q = parseInt(document.getElementById("admSetQ").value || "1", 10);
      const data = await fetchJson("/admin/state/set_current_question", { method: "POST", body: JSON.stringify({ current_question: q }) });
      log({ endpoint: "/admin/state/set_current_question", data });
      await refreshState();
      await refreshAdminAll();
    } catch (e) {
      logErr("adminSetCurrentQuestion", e);
    } finally {
      stopSpin();
    }
  }

  async function adminImportQuestions() {
    const fileEl = document.getElementById("admXlsxFile");
    if (!fileEl || !fileEl.files || !fileEl.files.length) {
      return log("xlsx 파일이 없습니다. 파일 선택 후 Upload를 눌러 주세요.");
    }

    const file = fileEl.files[0];
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      return log("xlsx만 업로드 가능합니다. (.xlsx)");
    }

    startSpin();
    try {
      const fd = new FormData();
      fd.append("file", file);
      const data = await fetchMultipart("/admin/questions/import", fd, {});
      log({ endpoint: "/admin/questions/import", data });
      await refreshAdminAll();
    } catch (e) {
      logErr("adminImportQuestions", e);
    } finally {
      stopSpin();
    }
  }

  async function personaGenerate() {
    startSpin();
    try {
      const model = (document.getElementById("personaModel").value || "").trim();
      const maxTokensRaw = (document.getElementById("personaMaxTokens").value || "").trim();
      const force = !!document.getElementById("personaForce").checked;

      const body = {};
      if (model) body.model = model;

      if (maxTokensRaw) {
        const n = parseInt(maxTokensRaw, 10);
        if (!isNaN(n) && n > 0) body.max_output_tokens = n;
      }

      if (force) body.force = true;

      const data = await fetchJson("/persona/generate", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/persona/generate", data });
      await refreshState();
      await refreshAdminAll();
    } catch (e) {
      logErr("personaGenerate", e);
    } finally {
      stopSpin();
    }
  }

  // Enter 전송(Shift+Enter 줄바꿈)
  document.getElementById("talkInput")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendTalk();
    }
  });

  // 초기 로드
  checkHealth();
  refreshState();
  fetchAdminProgress();
  loadTopics();
</script>

</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
def ui():
    return HTMLResponse(content=HTML)
