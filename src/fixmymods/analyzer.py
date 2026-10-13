from pathlib import Path

from .models import Diagnostic
from .rules import analyze_lines


def find_errors(path):
    try:
        with open(path, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return []

    errors = []

    for line in lines:
        if "error" in line.lower() or "exception" in line.lower():
            errors.append(line)

    return errors


def analyze_file(path: str | Path) -> list[Diagnostic]:
    try:
        lines = Path(path).read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
    except FileNotFoundError:
        return []

    return analyze_lines(lines)