# AGENTS.md — ESF Math 5-Star (启明星)

## Status
v0.9 — P0-P3 completed. Design docs:
- `design001.txt` — original project brief (scope, architecture, cost, timeline)
- `design002.txt` — deep design (UX, sprite, versions, API, tests, architecture)
- `design003.txt` — UX analysis v0.6 (3.6/10), 20-item improvement roadmap
- `design004.txt` — UX review round 1 v0.7 (5.4/10, +50%)
- `design005.txt` — UX review round 2 v0.8 (6.0/10, +67% total)
- `design006.txt` — UX review round 3 v0.9 (6.6/10, +83% total)

v0.1–v0.9 implemented. Code, build config, and tests exist with 117 backend / 34 frontend tests passing.

## Current version highlights (v0.9)
- **48 quiz questions** covering all 20 knowledge points (up from 10)
- **Knowledge graph visualization** in parent dashboard (SVG network by grade level)
- **Trend line charts** (accuracy + minutes over time, alongside bar chart)
- **Heatmap click interaction** with detail modal (mastery %, attempts, correct count)
- **3-slide onboarding** for first-time users (localStorage-gated)
- **Sprite entrance animation** (fly-in on homepage)
- **XP fly animation** (+N XP floating up on correct answer)
- **Daily goal celebration** (Canvas fireworks + sprite celebrate when progress hits 100%)
- **Sprite stage transition** animation (scale-in when leveling up stage)
- **6th sprite reaction** (thinking/book pose with thought bubbles, wiggle animation)
- **Share card** (daily summary shareable card with stats)
- **Haptic feedback** (5 vibration patterns via Vibration API)
- **Offline answer queue** (localStorage cache + sync on reconnect)
- **Push notification** subscription utilities (VAPID configured)
- **Multi-student support** (3 profiles, localStorage-persisted, dynamic API calls)
- **explanations.json** (20 KP detailed explanations with rules, mistakes, tips)
- **CorrectCount bug fixed** (independent state, no more off-by-one)
- All four agents + 8 API routers operational
- SQLite persistence (7 tables) via SharedStore write-through pattern

## Server
- IP: 101.96.217.150 (Ubuntu 24.04, Python 3.12, Node 22, 3.8GB RAM, 40G disk)
- Deploy target for this project

## Planned architecture (from design doc)

```
math-home-tutor/
├── backend/
│   ├── agents/          # Diagnostic, Planning, Teaching, Motivation agents
│   ├── engine/          # Knowledge graph (NetworkX), math verification (SymPy)
│   ├── data/            # JSON files: knowledge_graph, quiz_bank, explanations
│   ├── models/          # SQLAlchemy models (SQLite)
│   └── main.py          # FastAPI entrypoint
├── frontend/
│   └── src/
│       └── components/  # React + Vite + Tailwind, PWA via vite-plugin-pwa
├── knowledge_graph.json
├── quiz_bank.json
└── explanations.json
```

## Tech stack
- **Frontend**: React + Vite + Tailwind CSS, PWA (vite-plugin-pwa)
- **Backend**: Python 3.10+, FastAPI (async), single-process
- **Data**: SQLite via SQLAlchemy, NetworkX for graph traversal, SymPy for answer verification
- **LLM**: OpenAI / DeepSeek API (configured but NOT connected yet)
- **Deployment**: Gunicorn + Uvicorn + Nginx

## Design rules
- All four agents run in-process (no message queue in MVP).
- All AI-generated math answers must pass SymPy verification before reaching the student.
- Knowledge graph is loaded as a NetworkX DiGraph; BFS traces failure roots along `depends_on` edges.
- Tests follow TDD: Pytest (unit + integration), Playwright/Cypress (E2E), plus a custom LLM math-accuracy test suite.

## Session checkpoint (2026-05-06)
- **v0.8 UX review complete**: design005.txt shows 6.0/10 overall (up from 3.6 in v0.6).
- **P0 completed**: quiz bank 48 Qs, knowledge graph viz, heatmap click interaction.
- **P1 completed**: onboarding, sprite entrance/XP fly/goal celebration/stage transition animations.
- **Full flow working**: diagnose → report → learning path → quiz with hearts/combo/XP fly → daily summary → parent dashboard with graph.
- **Next step**: v1.0 milestone — remaining gaps:
  - Accessibility audit (aria labels, keyboard nav, screen reader)
  - Push notification end-to-end (register on server, daily reminder scheduling)
  - Drag-to-reorder learning path in parent dashboard
  - E2E Playwright tests (critical user journeys)
  - LLM pipeline (question generation + explanation generation)
- **First build commands**:
  - Backend: `pip install -e ".[dev]" && uvicorn backend.main:app --reload`
  - Frontend: `cd frontend && npm install && npm run dev`
  - Test: `pytest -v` / `cd frontend && npm run test`
- **Deploy target**: /opt/math-home-tutor on server, served via Nginx + Gunicorn/Uvicorn.
- venv: not created yet (global pip used). node_modules: frontend/node_modules exists.
