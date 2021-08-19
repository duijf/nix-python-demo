#!/usr/bin/env python
"""
Run lints before making commits.

USAGE

Run all lints, fixing any found problems automatically when
appropriate.

    ./pre-commit.py

Run all lints. Only report errors, don't fix them.

     ./pre-commit.py --check

Install this script as a pre-commit hook.

     ./pre-commit.py --install
"""

from __future__ import annotations

import enum
import os
import pathlib
import subprocess
import sys
from typing import List


class Mode(enum.Enum):
    FIX = "--fix"
    CHECK = "--check"
    INSTALL = "--install"

    @classmethod
    def from_cli(cls, cli_args: List[str]) -> Mode:
        arg_mode = cli_args[0] if len(cli_args) >= 1 else "--fix"
        return cls(arg_mode)


def run_lint(command: List[str], **kwargs) -> None:
    print(f"==> {command[0]}")
    try:
        subprocess.run(command, check=True, **kwargs)
    except subprocess.CalledProcessError:
        sys.exit(1)


def run_lints(mode: Mode) -> None:
    repo_root = os.environ["PROJECT_ROOT"]
    backend_root = f"{repo_root}/backend"

    check_mode = mode == Mode.CHECK
    extra_args = ["--check", "--diff"] if check_mode else []

    run_lint(["black"] + extra_args + ["--quiet", backend_root])
    run_lint(["isort"] + extra_args + ["--skip-gitignore", backend_root])
    run_lint(["flake8", backend_root + "/api"])
    run_lint(["mypy", "--strict", "--allow-redefinition", backend_root])
    run_lint(["pylint", "api", "tests"], cwd=backend_root)


def install_git_hook() -> None:
    script_contents = (
        "/usr/bin/env bash\n"
        "set -eufo pipefail\n"
        "$PROJECT_ROOT/bin/pre-commit.py --check\n"
    )

    repo_root = pathlib.Path(os.environ["PROJECT_ROOT"])
    script_file = repo_root / ".git" / "hooks" / "pre-commit"

    with script_file.open(mode="w") as f:
        f.write(script_contents)

    # Make the script executable, respecting permissions that were
    # previously there.
    current_perms = script_file.stat().st_mode
    script_file.chmod(current_perms | 0o111)


def main() -> None:
    mode = Mode.from_cli(sys.argv[1:])

    if mode == Mode.INSTALL:
        install_git_hook()
    else:
        run_lints(mode)


if __name__ == "__main__":
    main()
