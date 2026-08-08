from __future__ import annotations

import subprocess
from pathlib import Path

FORBIDDEN_FILES = {
    ".env",
    "config/chains.json",
    "config/getquin-token.txt",
}
FORBIDDEN_PREFIXES = ("crypto/", "real_estate/", "runtime/", "transactions/")


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = [path.replace("\\", "/") for path in result.stdout.split("\0") if path]
    violations = sorted(
        path
        for path in tracked
        if path in FORBIDDEN_FILES or path.startswith(FORBIDDEN_PREFIXES)
    )
    lock_text = Path("uv.lock").read_text(encoding="utf-8")
    if "file://" in lock_text or "editable =" in lock_text:
        violations.append("uv.lock contains a local or editable dependency")

    if violations:
        print("Unsafe workspace state:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print(f"Workspace validation passed for {len(tracked)} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
