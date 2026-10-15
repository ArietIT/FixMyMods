from fixmymods.analyzer import analyze_file


def test_analyze_file_finds_incompatible_mods(tmp_path):
    log_file = tmp_path / "latest.log"
    log_file.write_text("[ERROR] Incompatible mods found!\n", encoding="utf-8")

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


def test_analyze_file_finds_multiple_problems(tmp_path):
    log_file = tmp_path / "latest.log"
    log_file.write_text(
        "Incompatible mods found!\n"
        "Mod examplemod requires libexample, which is missing!\n"
        "java.lang.ClassNotFoundException: net.example.ModClass\n",
        encoding="utf-8",
    )

    diagnostics = analyze_file(log_file)

    assert {diagnostic.rule_id for diagnostic in diagnostics} == {
        "incompatible-mods",
        "missing-dependency",
        "missing-java-class",
    }


def test_analyze_file_detects_unsupported_java_version(tmp_path):
    log_file = tmp_path / "latest.log"
    log_file.write_text(
        "java.lang.IllegalArgumentException: Unsupported class file major version 61\n",
        encoding="utf-8",
    )

    diagnostics = analyze_file(log_file)

    assert any(d.rule_id == "unsupported-java-version" for d in diagnostics)
