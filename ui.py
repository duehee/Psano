from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

HTML = """
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
          <div class="title">Session / Teach / Talk</div>
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
            <span class="kbd">Tip: Start → Teach → Talk 순서로 누르면 됨</span>
          </div>

          <div class="sep"></div>

          <div class="card" style="box-shadow:none; background: var(--panel2);">
            <div class="hd">
              <div class="title">Teach (A/B)</div>
              <div class="row">
                <button onclick="getTeachQuestion()">Get question</button>
                <span id="qBadge" class="badge mono">question_id: -</span>
              </div>
            </div>
            <div class="body">
              <div id="teachQuestion" class="out muted small">아직 질문 없음</div>
              <div class="sep"></div>
              <div class="two">
                <button class="primary" onclick="sendTeachAnswer('A')">Choose A</button>
                <button onclick="sendTeachAnswer('B')">Choose B</button>
              </div>
              <div class="sub" style="margin-top:10px">
                선택하면 서버가 state를 업데이트하고, 응답 스키마(status/ui_text/stage/values)를 돌려줌.
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
              <textarea id="talkInput" placeholder="여기에 질문 입력... (예: 사노야 너는 누구야?)"></textarea>
              <div class="sep"></div>
              <div id="talkOutput" class="out muted small">아직 응답 없음</div>
              <div class="sub" style="margin-top:10px">
                OpenAI 실패/지연이면 fallback(status=fallback)로 내려옴.
              </div>
            </div>
          </div>
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
            <div class="badge mono">stage: <span id="stageVal">-</span></div>
            <div class="badge mono">teach_count: <span id="teachCount">-</span></div>
            <div class="badge mono">talk_count: <span id="talkCount">-</span></div>
          </div>
          <div class="sep"></div>
          <div class="out mono small" id="log"></div>
          <div class="sub" style="margin-top:12px">
            엔드포인트가 <span class="mono">/session/start</span>가 아니라 <span class="mono">/start</span>로 되어 있어도 자동으로 fallback 시도함.
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
  const teachQuestion = document.getElementById("teachQuestion");
  const talkOutput = document.getElementById("talkOutput");
  const logEl = document.getElementById("log");

  function setPill(state, text) {
    pill.classList.remove("status-ok", "status-warn", "status-bad");
    pill.classList.add(state);
    pill.querySelector("span.mono").textContent = text;
  }

  function log(obj) {
    const t = new Date().toLocaleTimeString();
    const s = (typeof obj === "string") ? obj : JSON.stringify(obj, null, 2);
    logEl.textContent = `[${t}] ${s}\\n\\n` + logEl.textContent;
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
      throw new Error(`${res.status} ${detail}`);
    }
    return data;
  }

  async function tryEndpoints(paths, options) {
    let lastErr = null;
    for (const p of paths) {
      try {
        const data = await fetchJson(p, options);
        return { path: p, data };
      } catch (e) {
        lastErr = e;
      }
    }
    throw lastErr || new Error("No endpoint worked");
  }

  async function checkHealth() {
    startSpin();
    try {
      const data = await fetchJson("/health");
      setPill("status-ok", "health: ok");
      log({ endpoint: "/health", data });
    } catch (e) {
      setPill("status-bad", "health: error");
      log("health error: " + e.message);
    } finally {
      stopSpin();
    }
  }

  function setExample() {
    document.getElementById("talkInput").value = "사노야, 너는 지금 무엇을 배우고 있어?";
  }

  function setSession(id) {
    sessionId = id;
    sessionBadge.textContent = `session_id: ${id || "-"}`;
  }

  function setQuestion(id, text) {
    lastQuestionId = id;
    qBadge.textContent = `question_id: ${id ?? "-"}`;
    teachQuestion.textContent = text || "아직 질문 없음";
  }

  function updateStatePanel(st) {
    if (!st) return;
    document.getElementById("stageVal").textContent = st.stage ?? "-";
    document.getElementById("teachCount").textContent = st.total_teach_count ?? "-";
    document.getElementById("talkCount").textContent = st.total_talk_count ?? "-";
  }

  async function startSession() {
    startSpin();
    try {
      const { path, data } = await tryEndpoints(
        ["/session/start", "/start"],
        { method: "POST", body: JSON.stringify({}) }
      );
      setSession(data.session_id);
      log({ endpoint: path, data });
      await refreshState();
    } catch (e) {
      log("startSession error: " + e.message);
    } finally {
      stopSpin();
    }
  }

  async function endSession() {
    if (!sessionId) return log("세션 없음. 먼저 Start를 클릭해봐.");
    startSpin();
    try {
      const body = { session_id: sessionId, reason: "completed" };
      const { path, data } = await tryEndpoints(
        ["/session/end", "/end"],
        { method: "POST", body: JSON.stringify(body) }
      );
      log({ endpoint: path, data });
      setSession(null);
      setQuestion(null, "아직 질문 없음");
      talkOutput.textContent = "아직 응답 없음";
      await refreshState();
    } catch (e) {
      log("endSession error: " + e.message);
    } finally {
      stopSpin();
    }
  }

  async function getTeachQuestion() {
    if (!sessionId) return log("세션 없음. 먼저 Start를 선택해봐.");
    startSpin();
    try {
      const url1 = `/teach/question?session_id=${encodeURIComponent(sessionId)}`;
      const data = await fetchJson(url1);
      const text = `${data.text}\\n\\nA) ${data.a_text}\\nB) ${data.b_text}`;
      setQuestion(data.question_id, text);
      log({ endpoint: "/teach/question", data });
    } catch (e) {
      log("getTeachQuestion error: " + e.message);
    } finally {
      stopSpin();
    }
  }

  async function sendTeachAnswer(choice) {
    if (!sessionId) return log("세션 없음. 먼저 Start를 선택해봐.");
    if (!lastQuestionId) return log("질문 없음. Get question 먼저 눌러줘.");
    startSpin();
    try {
      const body = { session_id: sessionId, question_id: lastQuestionId, choice };
      const data = await fetchJson("/teach/answer", { method: "POST", body: JSON.stringify(body) });
      log({ endpoint: "/teach/answer", data });
      // 다음 질문 준비용
      setQuestion(null, "(저장 완료) Get Question을 통해 새 질문을 가져올 수 있어.");
      await refreshState();
    } catch (e) {
      log("sendTeachAnswer error: " + e.message);
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
      log("sendTalk error: " + e.message);
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
      log("refreshState error: " + e.message);
    } finally {
      stopSpin();
    }
  }

  // 페이지 로드 시 health 한번
  checkHealth();
</script>

</body>
</html>
"""

@router.get("", response_class=HTMLResponse)
def ui():
    return HTMLResponse(content=HTML)