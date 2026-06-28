from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pymysql
from pymysql.cursors import DictCursor


BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "schema.mysql.sql"

class DatabaseError(Exception):
    pass


class IntegrityError(DatabaseError):
    pass


def mysql_config(include_database: bool = True) -> dict[str, Any]:
    config = {
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": False,
    }
    if include_database:
        config["database"] = os.environ.get("DB_NAME", "jeommechu")
    return config


def translate_sql(sql: str) -> str:
    sql = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", r"%(\1)s", sql)
    return sql.replace("?", "%s")


class Result:
    def __init__(self, cursor: Any):
        self._cursor = cursor
        self.rowcount = cursor.rowcount

    def fetchone(self) -> dict[str, Any] | None:
        return self._cursor.fetchone()

    def fetchall(self) -> list[dict[str, Any]]:
        return list(self._cursor.fetchall())


class MySQLConnection:
    def __init__(self) -> None:
        self._depth = 0
        try:
            self._conn = pymysql.connect(**mysql_config())
        except pymysql.err.IntegrityError as exc:
            raise IntegrityError(str(exc)) from exc
        except pymysql.MySQLError as exc:
            raise DatabaseError(str(exc)) from exc

    def __enter__(self) -> "MySQLConnection":
        self._depth += 1
        return self

    def __exit__(self, exc_type: Any, exc: BaseException | None, traceback: Any) -> None:
        self._depth -= 1
        if self._depth > 0:
            return
        try:
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        finally:
            self._conn.close()

    def execute(self, sql: str, params: Any = None) -> Result:
        try:
            cursor = self._conn.cursor()
            cursor.execute(translate_sql(sql), params)
            return Result(cursor)
        except pymysql.err.IntegrityError as exc:
            raise IntegrityError(str(exc)) from exc
        except pymysql.MySQLError as exc:
            raise DatabaseError(str(exc)) from exc

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()


def connect() -> MySQLConnection:
    return MySQLConnection()


def strip_sql_comments(script: str) -> str:
    return "\n".join(
        line for line in script.splitlines()
        if not line.strip().lstrip("\ufeff").startswith("--")
    )


def split_sql_script(script: str) -> list[str]:
    script = strip_sql_comments(script)
    statements = []
    current = []
    in_single = False
    in_double = False
    previous = ""
    for char in script:
        if char == "'" and not in_double and previous != "\\":
            in_single = not in_single
        elif char == '"' and not in_single and previous != "\\":
            in_double = not in_double
        if char == ";" and not in_single and not in_double:
            statement = "".join(current).strip()
            if statement and not statement.startswith("--"):
                statements.append(statement)
            current = []
        else:
            current.append(char)
        previous = char
    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


def ensure_database_exists() -> None:
    db_name = os.environ.get("DB_NAME", "jeommechu")
    if not re.fullmatch(r"[A-Za-z0-9_]+", db_name):
        raise DatabaseError("DB_NAME may contain only letters, numbers, and underscores")
    try:
        conn = pymysql.connect(**mysql_config(include_database=False))
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
                )
            conn.commit()
    except pymysql.MySQLError as exc:
        raise DatabaseError(str(exc)) from exc


def init_db() -> None:
    ensure_database_exists()
    script = SCHEMA_PATH.read_text(encoding="utf-8-sig")
    with connect() as conn:
        for statement in split_sql_script(script):
            conn.execute(statement)
