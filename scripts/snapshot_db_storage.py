"""Create a stable copy of a WeChat db_storage tree.

The source is read only. A snapshot is accepted only when the complete source
inventory is unchanged during the copy and the destination matches it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path


def inventory(root: Path) -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            result[path.relative_to(root).as_posix()] = (stat.st_size, stat.st_mtime_ns)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--attempts", type=int, default=4)
    args = parser.parse_args()

    source = args.source.resolve(strict=True)
    destination = args.destination.resolve(strict=False)
    if source.name.lower() != "db_storage":
        raise RuntimeError("Source must be an explicit db_storage directory")
    if destination == source or source in destination.parents:
        raise RuntimeError("Destination must be outside the source tree")
    destination.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, max(1, args.attempts) + 1):
        before = inventory(source)
        shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=shutil.copy2)
        after = inventory(source)
        changed = [
            name
            for name in sorted(set(before) | set(after))
            if before.get(name) != after.get(name)
        ]
        if not changed:
            copied = inventory(destination)
            mismatched = [name for name, signature in after.items() if copied.get(name) != signature]
            extra = sorted(set(copied) - set(after))
            if not mismatched and not extra:
                print(
                    json.dumps(
                        {
                            "status": "stable_snapshot_created",
                            "attempt": attempt,
                            "files": len(copied),
                            "bytes": sum(size for size, _mtime in copied.values()),
                        }
                    )
                )
                return 0
        print(
            json.dumps(
                {
                    "status": "source_changed_during_copy",
                    "attempt": attempt,
                    "changed_files": len(changed),
                }
            )
        )
        time.sleep(0.5)
    raise RuntimeError("Could not obtain a stable db_storage snapshot")


if __name__ == "__main__":
    raise SystemExit(main())
