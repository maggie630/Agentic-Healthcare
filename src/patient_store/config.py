from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

def database_path() -> Path:
    raw = os.getenv("DATABASE_PATH", "data/hospital.db")
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path

def mcp_host() -> str:
    return os.getenv("MCP_HOST", "127.0.0.1")

def mcp_port() -> int:
    try:
        port = int(os.getenv("MCP_PORT", "3001"))
    except ValueError as exc:
        raise ValueError("MCP_PORT must be an integer") from exc
    if not 1 <= port <= 65535:
        raise ValueError("MCP_PORT must be between 1 and 65535")
    return port

def approval_token() -> str:
    return os.getenv("APPROVAL_TOKEN", "")
