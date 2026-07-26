#!/usr/bin/env python3
"""Run the skill test suites, one pytest process per skill.

Separate processes are required, not a preference: skills' `scripts/`
directories share top-level module names (see tests/conftest.py).

    python tests/run_all.py                     # every skill under tests/
    python tests/run_all.py qutip pydicom       # only the named skills
    python tests/run_all.py -- -x --tb=long     # pass extra args to pytest

Exit code is 0 only when every suite passes. Suites that collect nothing are
reported as "empty" and do not fail the run.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent

NO_TESTS_COLLECTED = 5


def discover(names: list[str]) -> list[Path]:
    available = sorted(
        path
        for path in TESTS_DIR.iterdir()
        if path.is_dir() and not path.name.startswith((".", "__"))
    )
    if not names:
        return available
    by_name = {path.name: path for path in available}
    unknown = [name for name in names if name not in by_name]
    if unknown:
        sys.exit(
            f"no test directory for: {', '.join(unknown)}\n"
            f"available: {', '.join(sorted(by_name))}"
        )
    return [by_name[name] for name in names]


def main(argv: list[str]) -> int:
    if "--" in argv:
        separator = argv.index("--")
        names, pytest_args = argv[:separator], argv[separator + 1 :]
    else:
        names, pytest_args = argv, []

    suites = discover(names)
    results: dict[str, int] = {}
    for suite in suites:
        print(f"\n=== {suite.name} " + "=" * max(0, 60 - len(suite.name)))
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", str(suite.relative_to(REPO_ROOT)), *pytest_args],
            cwd=REPO_ROOT,
        )
        results[suite.name] = completed.returncode

    failed = {name: code for name, code in results.items() if code not in (0, NO_TESTS_COLLECTED)}
    empty = [name for name, code in results.items() if code == NO_TESTS_COLLECTED]

    print("\n" + "=" * 68)
    print(f"{len(results) - len(failed) - len(empty)} passed, {len(failed)} failed", end="")
    print(f", {len(empty)} empty" if empty else "")
    for name, code in sorted(failed.items()):
        print(f"  FAILED {name} (pytest exit {code})")
    for name in sorted(empty):
        print(f"  empty  {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
