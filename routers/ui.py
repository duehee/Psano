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

    /* file input은 width 100%면 너무 커서 예쁘게 조정 */
    input[type="file"] { width: auto; padding: 8px 10px; }

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

    /* admin sessions table 느낌 */
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

    /* checkbox styling(대충) */
    .chk {
      display:inline-flex;
      gap:6px;
      align-items:center;
      font-size:12px;
      color: rgba(255,255,255,0.75);
      user-select:none;
    }
    .chk input { width:auto; }

    /* 작은 도움 텍스트 */
    .hint {
      font-size: 12px;
      color: rgba(255,255,255,0.62);
      line-height: 1.4;
      margin-top: 8px;
    }
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
            <span class="kbd">Tip: Start(이름) → Question → Answer 반복 → chat되면 Talk</span>
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
                Start는 <span class="mono">POST /session/start</span>로 <span class="mono">visitor_name</span>을 먼저 입력해줘.
              </div>
            </div>
          </div>

          <div class="sep"></div>

          <div class="card" style="box-shadow:none; background: var(--panel2);">
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
                <span class="mono">GET /question/current</span>로 받고, <span class="mono">POST /answer</span>로 저장해.
              </div>
            </div>
          </div>

          <div class="sep"></div>

          <div class="card" style="box-shadow:none; background: var(--panel2);">
            <div class="hd">
              <div class="title">Talk (GPT)</div>
              <div class="row">
                <button class="primary" onclick="sendTalk()">Send</button>
                <button class="ghost" onclick="setExample()">Example</button>
              </div>
            </div>
            <div class="body">
              <textarea id="talkInput" placeholder="여기에 질문 입력... (chat phase에서만 동작)"></textarea>
              <div class="sep"></div>
              <div id="talkOutput" class="out muted small">아직 응답 없음</div>
              <div class="sub" style="margin-top:10px">
                formation 단계면 Talk은 사용할 수 없는게 정상(409).
              </div>
            </div>
          </div>

          <!-- Admin(운영자) 패널 -->
          <div class="sep"></div>

          <div class="card" style="box-shadow:none; background: var(--panel2);">
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

              <!-- reset controls -->
              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Reset</div>
                  <div class="sub">POST <span class="mono">/admin/reset</span></div>
                </div>
                <div class="row">
                  <label class="chk"><input id="resetAnswers" type="checkbox" /> answers</label>
                  <label class="chk"><input id="resetSessions" type="checkbox" /> sessions</label>
                  <label class="chk"><input id="resetState" type="checkbox" checked /> state</label>
                  <button class="danger" onclick="adminReset()">Reset</button>
                </div>
              </div>

              <div class="sep"></div>

              <!-- phase set -->
              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Phase set (test)</div>
                  <div class="sub">POST <span class="mono">/admin/phase/set</span></div>
                </div>
                <div class="row" style="min-width: 240px;">
                  <select id="admPhaseSelect" style="padding:10px 12px; border-radius:14px; border:1px solid var(--line); background: rgba(0,0,0,0.22); color: var(--text);">
                    <option value="formation">formation</option>
                    <option value="chat">chat</option>
                  </select>
                  <button onclick="adminSetPhase()">Apply</button>
                </div>
              </div>

              <div class="sep"></div>

              <!-- set current question -->
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

              <!-- NEW: Questions import (xlsx) -->
              <div class="row" style="width:100%">
                <div style="flex:1; min-width: 220px;">
                  <div class="muted small">Questions import (xlsx)</div>
                  <div class="sub">POST <span class="mono">/admin/questions/import</span></div>
                </div>
                <div class="row" style="width:100%">
                  <!--
                  <input id="admAdminToken" class="mono" placeholder="X-Admin-Token (optional)" style="max-width:260px" />
                  -->
                  <input id="admXlsxFile" type="file" accept=".xlsx" />
                  <button class="primary" onclick="adminImportQuestions()">Upload</button>
                </div>
                <div class="hint">
                  엑셀(.xlsx)을 올리면 <span class="mono">questions</span> 테이블이 upsert
                  결과(성공/실패)는 오른쪽 Debug 로그에 찍힘
                </div>
              </div>
              <!-- NEW end -->

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
          <!-- Admin 끝 -->
        </div>
      </section>

      <!-- Right: debug panel -->
      <aside class="card">
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
            현재 UI는 새 엔드포인트에 맞춰서 동작함:
            <span class="mono">/session/start</span>,
            <span class="mono">/question/current</span>,
            <span class="mono">/answer</span>,
            <span class="mono">/state</span>,
            <span class="mono">/talk</span>,
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

  const spinner = document.getElementById("spinner");
  const pill = document.getElementById("healthPill");
  const sessionBadge = document.getElementById("sessionBadge");
  const qBadge = document.getElementById("qBadge");
  const questionBox = document.getElementById("questionBox");
  const talkOutput = document.getElementById("talkOutput");
  const logEl = document.getElementById("log");

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

  // multipart/form-data 업로드용 (Content-Type 수동 지정 금지)
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
  }

  function setSession(id) {
    sessionId = id;
    sessionBadge.textContent = `session_id: ${id || "-"}`;
  }

  // session_question_index 표시까지 지원하도록 확장(기존 호출 호환)
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
    if (!name) return log("visitor_name 비어있음. 이름을 입력해줘.");

    startSpin();
    try {
      const body = { visitor_name: name };
      const data = await fetchJson("/session/start", { method: "POST", body: JSON.stringify(body) });
      setSession(data.session_id);
      log({ endpoint: "/session/start", data });
      await refreshState();
    } catch (e) {
      logErr("startSession", e);
    } finally {
      stopSpin();
    }
  }

  async function endSession() {
    if (!sessionId) return log("세션이 없어. 먼저 Start를 클릭해봐.");
    startSpin();
    try {
      const body = { session_id: sessionId, reason: "completed" };
      const data = await fetchJson("/session/end", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/session/end", data });
      setSession(null);
      setQuestion(null, "아직 질문 없음");
      talkOutput.textContent = "아직 응답 없음";
      await refreshState();
      await refreshAdminAll();
    } catch (e) {
      logErr("endSession", e);
    } finally {
      stopSpin();
    }
  }

  async function getCurrentQuestion() {
    if (!sessionId) return log("세션이 없어. 먼저 Start를 선택해봐.");
    startSpin();
    try {
      // session_id query 필수
      const data = await fetchJson(`/question/current?session_id=${encodeURIComponent(sessionId)}`);

      const idx = data.session_question_index ?? null;

      // 표시 강화 (index + axis)
      let text =
        `[${idx ?? "-"} / 5]\n` +
        `${data.question_text}\n\n` +
        `A) ${data.choice_a}\n` +
        `B) ${data.choice_b}\n\n` +
        `axis_key: ${data.axis_key}`;

      // value 키를 내려주고 있다면 표시(없으면 조용히 무시)
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
    if (!sessionId) return log("세션이 없어. 먼저 Start를 선택해봐.");
    if (!lastQuestionId) return log("질문 없음. Get current question 먼저 눌러줘.");

    startSpin();
    try {
      const body = { session_id: sessionId, question_id: lastQuestionId, choice };
      const data = await fetchJson("/answer", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/answer", data });

      // reaction 먼저 표시
      if (data.assistant_reaction_text) {
        questionBox.textContent = data.assistant_reaction_text;
      }

      // 5회 도달이면 종료 안내
      if (data.session_should_end) {
        setQuestion(null, `(형성 완료) ${data.session_question_index ?? 5}/5. 이제 End 눌러서 세션 종료해줘.`);
      } else {
        setQuestion(null, `(저장 완료!) ${data.session_question_index ?? "-"}/5. 다음 질문은 Get current question 눌러서 가져와줘.`);
      }

      await refreshState();
      await fetchAdminProgress();
    } catch (e) {
      logErr("sendAnswer", e);
    } finally {
      stopSpin();
    }
  }

  async function sendTalk() {
    if (!sessionId) return log("세션 없음. 먼저 Start를 선택해봐.");
    const txt = document.getElementById("talkInput").value.trim();
    if (!txt) return log("talk input 비어있음");

    startSpin();
    try {
      const body = { session_id: sessionId, user_text: txt };
      const data = await fetchJson("/talk", { method: "POST", body: JSON.stringify(body) });
      talkOutput.textContent = data.ui_text || "(empty)";
      log({ endpoint: "/talk", data });
      await refreshState();
    } catch (e) {
      logErr("sendTalk", e);
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

  // Admin Mutations
  async function adminReset() {
    startSpin();
    try {
      const body = {
        reset_answers: !!document.getElementById("resetAnswers").checked,
        reset_sessions: !!document.getElementById("resetSessions").checked,
        reset_state: !!document.getElementById("resetState").checked,
      };
      const data = await fetchJson("/admin/reset", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/admin/reset", data });
      await refreshState();
      await refreshAdminAll();
      setQuestion(null, "아직 질문 없음");
      talkOutput.textContent = "아직 응답 없음";
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

  // xlsx 업로드로 questions import
  async function adminImportQuestions() {
    const fileEl = document.getElementById("admXlsxFile");

    // 토큰 input이 주석/삭제되어도 안전하게
    const tokenEl = document.getElementById("admAdminToken");
    const token = (tokenEl ? tokenEl.value : "").trim();

    if (!fileEl || !fileEl.files || !fileEl.files.length) {
      return log("xlsx 파일이 없어. 파일 선택 후 Upload 눌러줘.");
    }

    const file = fileEl.files[0];
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      return log("xlsx만 업로드 가능해. (.xlsx)");
    }

    startSpin();
    try {
      const fd = new FormData();
      fd.append("file", file);

      // headers는 항상 선언(없으면 {})
      const headers = {};
      if (token) headers["X-Admin-Token"] = token;

      const data = await fetchMultipart("/admin/questions/import", fd, headers);
      log({ endpoint: "/admin/questions/import", data });

      // 업로드 후 운영 정보 갱신
      await refreshAdminAll();
    } catch (e) {
      logErr("adminImportQuestions", e);
    } finally {
      stopSpin();
    }
  }

  // 페이지 로드 시 health + state + admin progress(가볍게)
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
