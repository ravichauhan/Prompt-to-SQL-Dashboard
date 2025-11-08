import os
import sqlite3
from pathlib import Path
from typing import List

from fastapi import HTTPException
from openai import OpenAI

from .models import PromptQueryResponse
from .prompts import build_prompt

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"


class SQLService:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        if not DB_PATH.exists():
            raise RuntimeError("Sample database missing. Run python backend/sample_data.py first.")
        self.client = OpenAI(api_key=api_key)

    @staticmethod
    def describe_schema() -> str:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            descriptions: List[str] = []
            for row in tables:
                table = row["name"]
                cols = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
                columns = ", ".join(f"{c['name']} {c['type']}" for c in cols)
                descriptions.append(f"{table}({columns})")
            return "\n".join(descriptions)
        finally:
            conn.close()

    def translate_to_sql(self, natural_language: str) -> str:
        prompt = build_prompt(natural_language=natural_language, schema_ddl=self.describe_schema())
        try:
            completion = self.client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.2,
            )
        except Exception as exc:  # pragma: no cover - upstream error bubble
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        sql = completion.output[0].content[0].text.strip()
        return sql.rstrip(";")

    @staticmethod
    def run_sql(sql: str) -> tuple[List[str], List[List[str]]:
        sanitized = sql.strip().lower()
        if not sanitized.startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT statements are allowed")
        if ";" in sql.strip().rstrip(";"):
            raise HTTPException(status_code=400, detail="Multiple statements detected")

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute(sql)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            formatted = [[str(row[col]) for col in columns] for row in rows]
            return columns, formatted
        except sqlite3.DatabaseError as exc:
            raise HTTPException(status_code=400, detail=f"SQL error: {exc}") from exc
        finally:
            conn.close()

    def prompt_and_query(self, natural_language: str) -> PromptQueryResponse:
        sql = self.translate_to_sql(natural_language)
        columns, rows = self.run_sql(sql)
        notes = "Results generated from sales.db demo dataset"
        return PromptQueryResponse(sql=sql, columns=columns, rows=rows, notes=notes)
