import re
from collections.abc import Iterable, Sequence
from typing import Protocol

from .models import Diagnostic


class DiagnosticRule(Protocol):
    def analyze(self, lines: Sequence[str]) -> list[Diagnostic]:
        ...


class IncompatibleModsRule:
    rule_id = "incompatible-mods"
    marker = "incompatible mods found!"

    def analyze(self, lines: Sequence[str]) -> list[Diagnostic]:
        evidence = tuple(
            line for line in lines if self.marker in line.casefold()
        )
        if not evidence:
            return []

        return [
            Diagnostic(
                rule_id=self.rule_id,
                title="Обнаружены несовместимые моды",
                description=(
                    "Загрузчик модов сообщает, что некоторые установленные "
                    "моды несовместимы друг с другом или с этой версией игры."
                ),
                severity="error",
                suggestions=(
                    "Найдите подробности о конфликте в логе или crash-report.",
                    "Убедитесь, что версии модов подходят для вашей версии Minecraft и загрузчика.",
                    "Обновите, удалите или замените моды, указанные в отчёте.",
                ),
                evidence=evidence,
            )
        ]


class MissingDependencyRule:
    rule_id = "missing-dependency"
    pattern = re.compile(
        r"\brequires\b.*\bwhich\s+is\s+missing\b",
        re.IGNORECASE,
    )

    def analyze(self, lines: Sequence[str]) -> list[Diagnostic]:
        evidence = tuple(
            line for line in lines if self.pattern.search(line)
        )
        if not evidence:
            return []

        return [
            Diagnostic(
                rule_id=self.rule_id,
                title="Не найдена зависимость мода",
                description=(
                    "Загрузчик модов сообщает, что установленному моду "
                    "требуется другой мод, которого нет."
                ),
                severity="error",
                suggestions=(
                    "Посмотрите в логе или crash-report название требуемого мода.",
                    "Установите его версию, совместимую с вашей версией Minecraft и загрузчика.",
                    "Если мод, которому нужна зависимость, не требуется, удалите его.",
                ),
                evidence=evidence,
            )
        ]


DEFAULT_RULES: tuple[DiagnosticRule, ...] = (
    IncompatibleModsRule(),
    MissingDependencyRule(),
)


def analyze_lines(
    lines: Iterable[str],
    rules: Sequence[DiagnosticRule] = DEFAULT_RULES,
) -> list[Diagnostic]:
    log_lines = tuple(lines)
    diagnostics = []
    for rule in rules:
        diagnostics.extend(rule.analyze(log_lines))
    return diagnostics