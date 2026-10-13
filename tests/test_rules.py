from fixmymods.rules import IncompatibleModsRule


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