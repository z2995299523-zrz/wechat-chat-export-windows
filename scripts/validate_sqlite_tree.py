"""Run read-only SQLite validation for every decrypted database in a tree."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def validate(path: Path, full: bool) -> dict[str, object]:
    result: dict[str, object] = {
        "path": path.as_posix(),
        "size": path.stat().st_size,
        "status": "error",
        "check": [],
        "tables": 0,
        "error": "",
    }
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        pragma = "integrity_check" if full else "quick_check"
        rows = [str(row[0]) for row in connection.execute(f"PRAGMA {pragma}")]
        result["check"] = rows
        result["tables"] = int(
            connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type IN ('table','view')"
            ).fetchone()[0]
        )
        result["status"] = "ok" if rows == ["ok"] else "failed"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if connection is not None:
            connection.close()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve(strict=True)
    databases = sorted(root.rglob("*.db"))
    results = [validate(path, args.full) for path in databases]
    payload = {
        "root": str(root),
        "mode": "integrity_check" if args.full else "quick_check",
        "total": len(results),
        "ok": sum(item["status"] == "ok" for item in results),
        "failed": sum(item["status"] != "ok" for item in results),
        "databases": results,
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0 if payload["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
