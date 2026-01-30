"""
모니터링 대시보드
- GET /monitor : HTML 대시보드 페이지
- GET /monitor/api/data : 모니터링 데이터 JSON
"""
from __future__ import annotations

import os
from collections import deque

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from util.utils import get_config

router = APIRouter()

MAX_QUESTIONS = 365


# =========================
# API
# =========================

@router.get("/api/data")
def get_monitor_data(db: Session = Depends(get_db)):
    """
    모니터링 대시보드용 종합 데이터
    """
    # 1) 현재 상태
    st = db.execute(
        text("""
            SELECT phase, current_question, global_turn_count, cycle_number,
                   formed_at, persona_prompt
            FROM psano_state WHERE id = 1
        """)
    ).mappings().first()

    max_questions = get_config(db, "max_questions", MAX_QUESTIONS)
    global_turn_max = get_config(db, "global_turn_max", 365)

    cycle_number = int(st.get("cycle_number") or 1) if st else 1
    global_turn_count = int(st.get("global_turn_count") or 0) if st else 0
    phase = st.get("phase", "teach") if st else "teach"

    # 현재 사이클 답변 수
    cnt_row = db.execute(
        text("SELECT COUNT(*) AS cnt FROM answers WHERE cycle_id = :cycle_id"),
        {"cycle_id": cycle_number}
    ).mappings().first()
    answered_count = int(cnt_row["cnt"]) if cnt_row else 0

    # 2) 활성 세션 수
    active_row = db.execute(
        text("SELECT COUNT(*) AS cnt FROM sessions WHERE ended_at IS NULL")
    ).mappings().first()
    active_sessions = int(active_row["cnt"]) if active_row else 0

    # 오늘 총 세션 수
    today_row = db.execute(
        text("SELECT COUNT(*) AS cnt FROM sessions WHERE DATE(started_at) = CURDATE()")
    ).mappings().first()
    today_sessions = int(today_row["cnt"]) if today_row else 0

    # 3) 최근 이벤트 로그 (app.log에서 읽기)
    recent_events = []
    try:
        log_path = "logs/app.log"
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = deque(f, maxlen=50)
                for line in lines:
                    if "[EVENT]" in line:
                        recent_events.append(line.strip())
            recent_events = recent_events[-20:]
            recent_events.reverse()
    except Exception:
        pass

    # 4) LLM 통계 (llm_raw.log에서 최근 응답 시간 추출)
    llm_stats = {"avg_elapsed_ms": 0, "total_calls": 0, "recent_calls": []}
    llm_raw_logs = []
    try:
        llm_log_path = "logs/llm_raw.log"
        if os.path.exists(llm_log_path):
            with open(llm_log_path, "r", encoding="utf-8") as f:
                lines = list(deque(f, maxlen=100))
                elapsed_times = []
                for line in lines:
                    if "[LLM][RESP]" in line and "elapsed=" in line:
                        try:
                            parts = line.split("|")
                            for p in parts:
                                if "elapsed=" in p:
                                    ms_str = p.split("=")[1].replace("ms", "").strip()
                                    elapsed_times.append(float(ms_str))
                                    break
                        except Exception:
                            pass
                if elapsed_times:
                    llm_stats["avg_elapsed_ms"] = round(sum(elapsed_times) / len(elapsed_times), 0)
                    llm_stats["total_calls"] = len(elapsed_times)
                    llm_stats["recent_calls"] = elapsed_times[-10:]

                # 최근 LLM 로그 (최근 30개)
                llm_raw_logs = [line.strip() for line in lines[-30:]]
                llm_raw_logs.reverse()
    except Exception:
        pass

    return {
        "state": {
            "phase": phase,
            "cycle_number": cycle_number,
            "current_question": int(st.get("current_question") or 1) if st else 1,
            "answered_count": answered_count,
            "max_questions": max_questions,
            "global_turn_count": global_turn_count,
            "global_turn_max": global_turn_max,
            "progress_percent": round(answered_count / max_questions * 100, 1) if max_questions > 0 else 0,
            "global_progress_percent": round(global_turn_count / global_turn_max * 100, 1) if global_turn_max > 0 else 0,
            "has_persona": bool(st.get("persona_prompt")) if st else False,
        },
        "sessions": {
            "active": active_sessions,
            "today_total": today_sessions,
        },
        "recent_events": recent_events,
        "llm_stats": llm_stats,
        "llm_raw_logs": llm_raw_logs,
    }


# =========================
# UI
# =========================

MONITOR_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="2">
  <title>Psano Monitor</title>
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
      padding: 24px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }

    .logo {
      font-size: 24px;
      font-weight: 700;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 20px;
      font-size: 13px;
      font-family: var(--mono);
      box-shadow: var(--shadow);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 24px;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .card-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--muted);
    }

    .card-body {
      padding: 20px;
    }

    .stat-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid var(--border);
    }

    .stat-row:last-child { border-bottom: none; }

    .stat-label {
      font-size: 14px;
      color: var(--muted);
    }

    .stat-value {
      font-size: 18px;
      font-weight: 600;
      font-family: var(--mono);
    }

    .stat-value.highlight { color: var(--accent); }
    .stat-value.warning { color: var(--warning); }
    .stat-value.danger { color: var(--danger); }

    .big-stat {
      text-align: center;
      padding: 16px 0;
    }

    .big-stat .value {
      font-size: 48px;
      font-weight: 700;
      font-family: var(--mono);
      line-height: 1;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .big-stat .label {
      font-size: 13px;
      color: var(--muted);
      margin-top: 8px;
    }

    .progress-bar {
      height: 8px;
      background: var(--secondary);
      border-radius: 4px;
      overflow: hidden;
      margin-top: 12px;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary), var(--accent));
      border-radius: 4px;
      transition: width 0.3s ease;
    }

    .progress-fill.warning {
      background: linear-gradient(90deg, var(--warning), var(--danger));
    }

    .phase-badge {
      display: inline-block;
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .phase-badge.teach {
      background: #eef2ff;
      color: var(--primary);
    }

    .phase-badge.talk {
      background: #ecfdf5;
      color: var(--accent);
    }

    .llm-chart {
      display: flex;
      align-items: flex-end;
      gap: 4px;
      height: 50px;
      margin-top: 12px;
      padding: 8px;
      background: var(--secondary);
      border-radius: var(--radius-sm);
    }

    .llm-bar {
      flex: 1;
      background: linear-gradient(180deg, var(--primary), var(--accent));
      border-radius: 2px 2px 0 0;
      min-height: 4px;
    }

    .log-box {
      background: #1e293b;
      color: #e2e8f0;
      border-radius: var(--radius-sm);
      padding: 16px;
      font-family: var(--mono);
      font-size: 11px;
      line-height: 1.7;
      max-height: 300px;
      overflow-y: auto;
    }

    .log-line {
      padding: 4px 0;
      border-bottom: 1px solid #334155;
    }

    .log-line:last-child { border-bottom: none; }

    .log-time { color: #64748b; }
    .log-tag { color: #60a5fa; font-weight: 600; }
    .log-tag.req { color: #fbbf24; }
    .log-tag.resp { color: #34d399; }
    .log-tag.content { color: #a78bfa; }
    .log-tag.error { color: #f87171; }
    .log-info { color: #94a3b8; }

    .event-list {
      max-height: 250px;
      overflow-y: auto;
    }

    .event-item {
      padding: 10px 0;
      border-bottom: 1px solid var(--border);
      font-size: 13px;
    }

    .event-item:last-child { border-bottom: none; }

    .event-time {
      font-family: var(--mono);
      font-size: 11px;
      color: var(--muted);
    }

    .event-name {
      font-weight: 600;
      color: var(--primary);
      margin-left: 8px;
    }

    .event-params {
      color: var(--muted);
      font-size: 12px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }

    @media (max-width: 900px) {
      .grid-2 { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">Psano Monitor</div>
    <div class="status-pill">
      <div class="status-dot"></div>
      <span id="lastUpdate">Loading...</span>
    </div>
  </div>

  <div class="grid">
    <!-- 현재 상태 -->
    <div class="card">
      <div class="card-header">Current State</div>
      <div class="card-body">
        <div class="stat-row">
          <span class="stat-label">Phase</span>
          <span id="phase" class="phase-badge teach">TEACH</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Cycle</span>
          <span id="cycle" class="stat-value">1</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Persona</span>
          <span id="hasPersona" class="stat-value">-</span>
        </div>
      </div>
    </div>

    <!-- 형성기 진행 -->
    <div class="card">
      <div class="card-header">Formation Progress</div>
      <div class="card-body">
        <div class="big-stat">
          <div class="value" id="formationProgress">0%</div>
          <div class="label"><span id="answered">0</span> / <span id="maxQuestions">365</span> answers</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" id="formationBar" style="width: 0%"></div>
        </div>
      </div>
    </div>

    <!-- 대화기 진행 -->
    <div class="card">
      <div class="card-header">Global Turn Progress</div>
      <div class="card-body">
        <div class="big-stat">
          <div class="value" id="globalProgress">0%</div>
          <div class="label"><span id="globalTurn">0</span> / <span id="globalMax">365</span> turns</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" id="globalBar" style="width: 0%"></div>
        </div>
      </div>
    </div>

    <!-- 세션 -->
    <div class="card">
      <div class="card-header">Sessions</div>
      <div class="card-body">
        <div class="stat-row">
          <span class="stat-label">Active Now</span>
          <span id="activeSessions" class="stat-value highlight">0</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Today Total</span>
          <span id="todaySessions" class="stat-value">0</span>
        </div>
      </div>
    </div>

    <!-- LLM 통계 -->
    <div class="card">
      <div class="card-header">LLM Stats</div>
      <div class="card-body">
        <div class="stat-row">
          <span class="stat-label">Avg Response</span>
          <span id="avgElapsed" class="stat-value">-</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Recent Calls</span>
          <span id="totalCalls" class="stat-value">0</span>
        </div>
        <div class="llm-chart" id="llmChart"></div>
      </div>
    </div>
  </div>

  <!-- 로그 섹션 -->
  <div class="grid-2">
    <!-- 이벤트 로그 -->
    <div class="card">
      <div class="card-header">Recent Events</div>
      <div class="card-body">
        <div class="event-list" id="eventsList">
          <div class="event-item" style="color: var(--muted);">No events yet</div>
        </div>
      </div>
    </div>

    <!-- LLM Raw 로그 -->
    <div class="card">
      <div class="card-header">LLM API Logs</div>
      <div class="card-body">
        <div class="log-box" id="llmLogs">
          <div class="log-line" style="color: #64748b;">No logs yet</div>
        </div>
      </div>
    </div>
  </div>

  <script>
    async function fetchData() {
      try {
        const res = await fetch('/monitor/api/data');
        const data = await res.json();
        updateUI(data);
        document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
      } catch (e) {
        console.error('Failed to fetch:', e);
      }
    }

    function updateUI(data) {
      const s = data.state;

      // Phase
      const phaseEl = document.getElementById('phase');
      phaseEl.textContent = s.phase.toUpperCase();
      phaseEl.className = 'phase-badge ' + s.phase;

      // Cycle & Persona
      document.getElementById('cycle').textContent = s.cycle_number;
      const personaEl = document.getElementById('hasPersona');
      personaEl.textContent = s.has_persona ? 'Yes' : 'No';
      personaEl.className = 'stat-value ' + (s.has_persona ? 'highlight' : '');

      // Formation
      document.getElementById('formationProgress').textContent = s.progress_percent + '%';
      document.getElementById('answered').textContent = s.answered_count;
      document.getElementById('maxQuestions').textContent = s.max_questions;
      document.getElementById('formationBar').style.width = s.progress_percent + '%';

      // Global
      document.getElementById('globalProgress').textContent = s.global_progress_percent + '%';
      document.getElementById('globalTurn').textContent = s.global_turn_count;
      document.getElementById('globalMax').textContent = s.global_turn_max;
      const globalBar = document.getElementById('globalBar');
      globalBar.style.width = s.global_progress_percent + '%';
      globalBar.className = 'progress-fill' + (s.global_progress_percent >= 90 ? ' warning' : '');

      // Sessions
      document.getElementById('activeSessions').textContent = data.sessions.active;
      document.getElementById('todaySessions').textContent = data.sessions.today_total;

      // LLM Stats
      const llm = data.llm_stats;
      document.getElementById('avgElapsed').textContent = llm.avg_elapsed_ms ? llm.avg_elapsed_ms + 'ms' : '-';
      document.getElementById('totalCalls').textContent = llm.total_calls;

      // LLM Chart
      const chartEl = document.getElementById('llmChart');
      if (llm.recent_calls && llm.recent_calls.length > 0) {
        const maxMs = Math.max(...llm.recent_calls, 3000);
        chartEl.innerHTML = llm.recent_calls.map(ms => {
          const h = Math.max(4, (ms / maxMs) * 40);
          return `<div class="llm-bar" style="height: ${h}px" title="${ms}ms"></div>`;
        }).join('');
      }

      // Events
      const eventsEl = document.getElementById('eventsList');
      if (data.recent_events && data.recent_events.length > 0) {
        eventsEl.innerHTML = data.recent_events.map(line => {
          const match = line.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[EVENT\] (\w+)(.*)$/);
          if (match) {
            const time = match[1].split(' ')[1];
            const name = match[2];
            const params = match[3] || '';
            return `<div class="event-item"><span class="event-time">${time}</span><span class="event-name">${name}</span><span class="event-params">${params}</span></div>`;
          }
          return `<div class="event-item">${line}</div>`;
        }).join('');
      }

      // LLM Raw Logs
      const logsEl = document.getElementById('llmLogs');
      if (data.llm_raw_logs && data.llm_raw_logs.length > 0) {
        logsEl.innerHTML = data.llm_raw_logs.map(line => {
          // Parse timestamp
          const timeMatch = line.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);
          const time = timeMatch ? timeMatch[1].split(' ')[1] : '';

          // Determine tag type
          let tagClass = '';
          let content = line;
          if (line.includes('[LLM][REQ]')) {
            tagClass = 'req';
            content = line.replace(/.*\[LLM\]\[REQ\]/, '[REQ]');
          } else if (line.includes('[LLM][RESP]')) {
            tagClass = 'resp';
            content = line.replace(/.*\[LLM\]\[RESP\]/, '[RESP]');
          } else if (line.includes('[LLM][CONTENT]')) {
            tagClass = 'content';
            content = line.replace(/.*\[LLM\]\[CONTENT\]/, '[CONTENT]');
          } else if (line.includes('[LLM][ERROR]') || line.includes('[LLM][FAILED]')) {
            tagClass = 'error';
            content = line.replace(/.*\[LLM\]\[(ERROR|FAILED)\]/, '[$1]');
          }

          if (tagClass) {
            const tag = content.match(/^\[(\w+)\]/)?.[1] || '';
            const rest = content.replace(/^\[\w+\]\s*/, '');
            return `<div class="log-line"><span class="log-time">${time}</span> <span class="log-tag ${tagClass}">[${tag}]</span> <span class="log-info">${rest}</span></div>`;
          }
          return `<div class="log-line">${line}</div>`;
        }).join('');
      }
    }

    // Initial fetch
    fetchData();
  </script>
</body>
</html>
"""


@router.get("", response_class=HTMLResponse)
def monitor_page():
    """모니터링 대시보드 페이지"""
    return HTMLResponse(content=MONITOR_HTML)
