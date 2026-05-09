# AGENTS.md — ESF Math 5-Star (启明星)

## Status
v1.0 — All milestones achieved (UX 7.0/10). Design docs:
- `design001.txt` — original project brief (scope, architecture, cost, timeline)
- `design002.txt` — deep design (UX, sprite, versions, API, tests, architecture)
- `design003.txt` — UX analysis v0.6 (3.6/10), 20-item improvement roadmap
- `design004.txt` — UX review round 1 v0.7 (5.4/10, +50%)
- `design005.txt` — UX review round 2 v0.8 (6.0/10, +67% total)
- `design006.txt` — UX review round 3 v0.9 (6.6/10, +83% total)
- `design007.txt` — UX review final v1.0 (7.0/10, +94% total)
- `design008.txt` — GAP filled v1.1 (7.3/10)
- `design009.txt` — v2.0 interaction & quiz design deep analysis

v0.1–v1.0 implemented. Code, build config, and tests exist with 117 backend / 34 frontend / 5 E2E tests passing.

## Current version highlights (v2.1)
- **Flutter + Flame Android/web app** with game engine
- **48 quiz questions** covering all 20 knowledge points
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
- **Push notification** subscription (registered via Service Worker, backend API)
- **Multi-student support** (3 profiles, localStorage-persisted, dynamic API calls)
- **explanations.json** (20 KP detailed explanations with rules, mistakes, tips)
- **Drag-to-reorder learning path** in parent dashboard (HTML5 drag-and-drop)
- **Accessibility** (19 fixes: aria-labels, keyboard nav, live regions, role attributes)
- **LLM pipeline** (DeepSeek API question generation + SymPy verification)
- **E2E Playwright tests** (5 critical user journeys)
- All four agents + 10 API routers operational
- SQLite persistence (8 tables) via SharedStore write-through pattern

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

## Session checkpoint (2026-05-08)
- **v2.0 progress**: Flutter + Flame Android/web app built.
  - Flutter 3.29.3, JDK 17, Android SDK 34, NDK 27
  - APK: 21MB release at http://101.96.217.150/flutter/app-release.apk
  - Web: http://101.96.217.150/flutter/
  - Screens: Home (sprite + stats + 4 cards), Diagnose, Quiz (hearts/combo), Parent (PIN 1234), Settings (version check + server config + student profile)
  - Game engine: Flame MathSprite with tap interaction, 5 evolution stages, particle effects
  - Storyteller: 8 themes, `/api/exercise/story` + `/api/exercise/themes`
  - Version API: `/api/health/version` for in-app update checks
  - Nginx: React at `/`, Flutter at `/flutter/` with `^~` prefix priority
- **v2.1**: Multi-agent review system + P0-P4 UX improvements + auto-upgrade
  - P0: Sound system (Web Audio API synthesized tones)
  - P1-P4: A11y Semantics, React sprite fix, report visualization, storyteller integration
  - Auto-upgrade: Settings page checks `/api/health/version`, downloads APK, triggers installer
  - Shorebird: CLI 1.6.98 installed and logged in
  - **Shorebird Release 1.0.0+1 published** + Patch 1 tested (v1.0.1)
  - Hot update flow: `shorebird patch android` → users get update on next app open
  - v1.0.1 deployed (version_code=2) on server
  - APK updated: quiz_screen 4.8 → 6.1, Semantics + storyteller + QuestionCard integration
- **v2.1 fix**: 12 quiz answers corrected (SymPy verification of all 200 Qs). Root cause: `MathVerifier.verify(question_text, answer)` was comparing question text as student answer. Fixed with `verify_question_answer()` that extracts math expressions and computes true answers.
- **v1.1.1**: All GAPs filled. Quiz bank 200 Qs. Component refactoring done.
- **Tests**: 132 backend / 44 UX API / 34 frontend all pass.
- **First build commands**:
  - Backend: `pip install -e ".[dev]" && uvicorn backend.main:app --reload`
  - Frontend: `cd frontend && npm install && npm run dev`
  - Test: `pytest -v` / `cd frontend && npm run test`
  - E2E: `cd frontend && npx playwright test`
- **Deploy target**: /opt/math-home-tutor on server, served via Nginx + Gunicorn/Uvicorn.
- venv: not created yet (global pip used). node_modules: frontend/node_modules exists.
