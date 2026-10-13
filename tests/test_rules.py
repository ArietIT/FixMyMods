from fixmymods.rules import IncompatibleModsRule, MissingDependencyRule


def test_incompatible_mods_rule_matches_case_insensitively():
    diagnostics = IncompatibleModsRule().analyze(
        ["[ERROR] Incompatible mods found!"]
    )

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "incompatible-mods"
    assert diagnostics[0].severity == "error"
    assert diagnostics[0].evidence == ("[ERROR] Incompatible mods found!",)
    assert diagnostics[0].suggestions


def test_incompatible_mods_rule_ignores_unrelated_lines():
    assert IncompatibleModsRule().analyze(
        ["A mod printed the word incompatible, but no loader report followed."]
    ) == []


def test_incompatible_mods_rule_keeps_all_matching_evidence():
    lines = [
        "Incompatible mods found!",
        "INCOMPATIBLE MODS FOUND!",
    ]

    diagnostics = IncompatibleModsRule().analyze(lines)

    assert len(diagnostics) == 1
    assert diagnostics[0].evidence == tuple(lines)


def test_missing_dependency_rule_matches_loader_report_case_insensitively():
    line = "Mod examplemod requires libexample, which is missing!"

    diagnostics = MissingDependencyRule().analyze([line])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "missing-dependency"
    assert diagnostics[0].severity == "error"
    assert diagnostics[0].evidence == (line,)
    assert diagnostics[0].suggestions
    uppercase_line = "MOD EXAMPLEMOD REQUIRES LIBEXAMPLE, WHICH IS MISSING!"
    uppercase_diagnostics = MissingDependencyRule().analyze([uppercase_line])
    assert uppercase_diagnostics[0].evidence == (uppercase_line,)


def test_missing_dependency_rule_ignores_unconfirmed_mentions():
    lines = [
        "Missing dependency warning from an unrelated mod.",
        "Mod examplemod requires libexample, which is installed.",
        "Mod examplemod is missing.",
    ]

    assert MissingDependencyRule().analyze(lines) == []


def test_missing_dependency_rule_keeps_all_matching_evidence():
    lines = [
        "Mod firstmod requires firstlib, which is missing!",
        "Mod secondmod requires secondlib, which is missing!",
    ]

    diagnostics = MissingDependencyRule().analyze(lines)

    assert len(diagnostics) == 1
    assert diagnostics[0].evidence == tuple(lines)