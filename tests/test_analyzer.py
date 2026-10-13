from fixmymods.analyzer import analyze_file


def test_analyze_file_finds_incompatible_mods(tmp_path):
    log_file = tmp_path / "latest.log"
    log_file.write_text(
        "[ERROR] Incompatible mods found!\n", encoding="utf-8"
    )

    diagnostics = analyze_file(log_file)

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "incompatible-mods"


def test_analyze_file_returns_no_diagnostics_for_missing_file(tmp_path):
    assert analyze_file(tmp_path / "missing.log") == []


def test_analyze_file_finds_missing_dependency(tmp_path):
    log_file = tmp_path / "latest.log"
    log_file.write_text(
        "Mod examplemod requires libexample, which is missing!\n",
        encoding="utf-8",
    )

    diagnostics = analyze_file(log_file)

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "missing-dependency"