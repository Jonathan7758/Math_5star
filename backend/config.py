import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/data.db")
KNOWLEDGE_GRAPH_PATH = os.getenv("KNOWLEDGE_GRAPH_PATH", str(DATA_DIR / "knowledge_graph.json"))
QUIZ_BANK_PATH = os.getenv("QUIZ_BANK_PATH", str(DATA_DIR / "quiz_bank.json"))
EXPLANATIONS_PATH = os.getenv("EXPLANATIONS_PATH", str(DATA_DIR / "explanations.json"))

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

DIAGNOSTIC_ERROR_THRESHOLD = float(os.getenv("DIAGNOSTIC_ERROR_THRESHOLD", "0.3"))
DIAGNOSTIC_BFS_MAX_DEPTH = int(os.getenv("DIAGNOSTIC_BFS_MAX_DEPTH", "5"))

PARENT_PIN = os.getenv("PARENT_PIN", "1234")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
