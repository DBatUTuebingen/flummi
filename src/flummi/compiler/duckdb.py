from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

type PathValue = str | os.PathLike[str]


def find_binary(binary: PathValue | None = None) -> str | None:
    return shutil.which(os.fspath(binary) if binary is not None else "duckdb")


@dataclass
class Result:
    rows: list[tuple[Any, ...]]

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.rows[0] if self.rows else None

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self.rows


class Connection:
    def __init__(
        self,
        binary: PathValue,
        database: PathValue | None = None,
    ) -> None:
        self.binary = os.fspath(binary)
        self.database = (
            os.fspath(database) if database is not None else ":memory:"
        )

    def execute(self, query: str) -> Result:
        command = [self.binary, "-no-init", "-bail", "-json"]
        if self.database != ":memory:":
            command.append("-readonly")
        command.extend((self.database, "-c", query))

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
            )
        except OSError as error:
            raise RuntimeError(
                f"Could not execute DuckDB binary {self.binary!r}: {error}"
            ) from error

        if completed.returncode != 0:
            diagnostic = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(
                f"DuckDB binary exited with status {completed.returncode}: "
                f"{diagnostic}"
            )

        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"DuckDB binary returned invalid JSON: {completed.stdout!r}"
            ) from error

        if not isinstance(result, list) or not all(
            isinstance(row, dict) for row in result
        ):
            raise RuntimeError(
                f"DuckDB binary returned an unexpected JSON result: {result!r}"
            )

        return Result([tuple(row.values()) for row in result])
