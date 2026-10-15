import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from fixmymods.gui import MainWindow


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


def test_gui_displays_diagnostics_from_selected_file(tmp_path, app):
    log_file = tmp_path / "latest.log"
    log_file.write_text(
        "Mod examplemod requires libexample, which is missing!\n",
        encoding="utf-8",
    )
    window = MainWindow()
    window.set_log_file(log_file)
    window.analyze_selected_file()

    assert window.diagnostics_list.count() == 1
    assert "Не найдена зависимость мода" in window.diagnostics_list.item(0).text()
    assert "Строки из файла" in window.details_view.toPlainText()


def test_gui_explains_when_no_known_problem_is_found(tmp_path, app):
    log_file = tmp_path / "latest.log"
    log_file.write_text("[INFO] Minecraft started\n", encoding="utf-8")
    window = MainWindow()
    window.set_log_file(log_file)
    window.analyze_selected_file()

    assert window.diagnostics_list.count() == 0
    assert "не обнаружены" in window.details_view.toPlainText()


def test_gui_reports_a_missing_file(tmp_path, app, monkeypatch):
    window = MainWindow()
    existing_log = tmp_path / "latest.log"
    existing_log.write_text("Incompatible mods found!\n", encoding="utf-8")
    window.set_log_file(existing_log)
    window.analyze_selected_file()
    assert window.diagnostics_list.count() == 1

    window.set_log_file(tmp_path / "missing.log")
    messages = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args: messages.append(args[-1]),
    )

    window.analyze_selected_file()

    assert len(messages) == 1
    assert "Файл не найден" in messages[0]
    assert window.diagnostics_list.count() == 0


def test_gui_surfaces_read_errors(tmp_path, app, monkeypatch):
    log_file = tmp_path / "latest.log"
    log_file.write_text("log", encoding="utf-8")
    window = MainWindow()
    window.set_log_file(log_file)
    messages = []
    monkeypatch.setattr(
        "fixmymods.gui.analyze_file",
        lambda path: (_ for _ in ()).throw(PermissionError("access denied")),
    )
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args: messages.append(args[-1]),
    )

    window.analyze_selected_file()

    assert len(messages) == 1
    assert "access denied" in messages[0]
