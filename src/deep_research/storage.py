"""SQLite persistence для исследований."""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional

from deep_research.state import ResearchState, Finding


class ResearchStorage:
    """Хранилище исследований в SQLite."""
    
    def __init__(self, db_path: str = "data/research.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Инициализация схемы БД."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS research_sessions (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    source TEXT,
                    url TEXT,
                    title TEXT,
                    content TEXT,
                    score REAL,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES research_sessions(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_sessions_status 
                    ON research_sessions(status);
            """)
    
    def save_session(self, state: ResearchState) -> None:
        """Сохраняет или обновляет сессию."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO research_sessions 
                (id, query, state_json, status, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    state.session_id,
                    state.query,
                    state.model_dump_json(),
                    state.status
                )
            )
    
    def load_session(self, session_id: str) -> Optional[ResearchState]:
        """Загружает сессию по ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT state_json FROM research_sessions WHERE id = ?",
                (session_id,)
            ).fetchone()
            
            if row:
                return ResearchState.model_validate_json(row[0])
            return None
    
    def list_sessions(self, status: Optional[str] = None) -> List[tuple]:
        """Список сессий."""
        with sqlite3.connect(self.db_path) as conn:
            if status:
                rows = conn.execute(
                    """SELECT id, query, status, created_at, updated_at 
                       FROM research_sessions WHERE status = ?
                       ORDER BY updated_at DESC""",
                    (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, query, status, created_at, updated_at 
                       FROM research_sessions
                       ORDER BY updated_at DESC"""
                ).fetchall()
            return rows
    
    def save_finding(self, session_id: str, finding: Finding) -> None:
        """Сохраняет найденный источник."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO findings 
                (session_id, source, url, title, content, score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    finding.source,
                    finding.url,
                    finding.title,
                    finding.content,
                    finding.score,
                    json.dumps(finding.metadata)
                )
            )
    
    def load_findings(self, session_id: str) -> List[Finding]:
        """Загружает все источники для сессии."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT source, url, title, content, score, metadata 
                   FROM findings WHERE session_id = ?""",
                (session_id,)
            ).fetchall()
            
            findings = []
            for row in rows:
                findings.append(Finding(
                    source=row[0],
                    url=row[1],
                    title=row[2],
                    content=row[3],
                    score=row[4],
                    metadata=json.loads(row[5]) if row[5] else {}
                ))
            return findings
