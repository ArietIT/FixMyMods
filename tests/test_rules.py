from fixmymods.rules import (
    IncompatibleModsRule,
    MainClassLoadErrorRule,
    MixinConflictRule,
    MissingDependencyRule,
    MissingJavaClassRule,
    MissingNativeLibraryRule,
    MethodMismatchRule,
    UnsupportedJavaVersionRule,
)


def test_incompatible_mods_rule_matches_case_insensitively():
    diagnostics = IncompatibleModsRule().analyze(["[ERROR] Incompatible mods found!"])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "incompatible-mods"
    assert diagnostics[0].severity == "error"
    assert diagnostics[0].evidence == ("[ERROR] Incompatible mods found!",)
    assert diagnostics[0].suggestions


def test_incompatible_mods_rule_ignores_unrelated_lines():
    assert IncompatibleModsRule().analyze([
        "A mod printed the word incompatible, but no loader report followed."
    ]) == []


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


def test_missing_java_class_rule_detects_class_not_found():
    diagnostics = MissingJavaClassRule().analyze([
        "java.lang.NoClassDefFoundError: com/example/ModClass"
    ])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "missing-java-class"
    assert diagnostics[0].severity == "error"


def test_unsupported_java_version_rule_detects_class_version_issue():
    diagnostics = UnsupportedJavaVersionRule().analyze([
        "java.lang.IllegalArgumentException: Unsupported class file major version 61"
    ])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "unsupported-java-version"
    assert diagnostics[0].severity == "warning"


def test_missing_native_library_rule_detects_unsupported_link():
    diagnostics = MissingNativeLibraryRule().analyze([
        "java.lang.UnsatisfiedLinkError: no lwjgl64 in java.library.path"
    ])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "missing-native-library"
    assert diagnostics[0].severity == "error"


def test_method_mismatch_rule_detects_loader_conflict():
    diagnostics = MethodMismatchRule().analyze([
        "java.lang.NoSuchMethodError: net.example.ModClass.method()V"
    ])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "method-mismatch"
    assert diagnostics[0].severity == "error"


def test_main_class_load_error_rule_detects_launch_failure():
    diagnostics = MainClassLoadErrorRule().analyze([
        "Error: Unable to load main class net.minecraft.client.main.Main"
    ])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "main-class-load-error"
    assert diagnostics[0].severity == "error"


def test_mixin_conflict_rule_detects_transformer_error():
    diagnostics = MixinConflictRule().analyze([
        "Mixin transformation failed: mod examplemod" 
    ])

    assert len(diagnostics) == 1
    assert diagnostics[0].rule_id == "mixin-conflict"
    assert diagnostics[0].severity == "error"
