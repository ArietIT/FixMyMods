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
                title="Incompatible mods found",
                description=(
                    "The mod loader reported that some installed mods "
                    "cannot be used together or with this game setup."
                ),
                severity="error",
                suggestions=(
                    "Review the incompatibility details in the log or crash report.",
                    "Check that each mod supports your Minecraft and mod-loader versions.",
                    "Update, remove, or replace the mods identified by the report.",
                ),
                evidence=evidence,
            )
        ]


DEFAULT_RULES: tuple[DiagnosticRule, ...] = (IncompatibleModsRule(),)


def analyze_lines(
    lines: Iterable[str],
    rules: Sequence[DiagnosticRule] = DEFAULT_RULES,
) -> list[Diagnostic]:
    log_lines = tuple(lines)
    diagnostics = []
    for rule in rules:
        diagnostics.extend(rule.analyze(log_lines))
    return diagnostics