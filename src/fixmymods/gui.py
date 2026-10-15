from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .analyzer import analyze_file
from .models import Diagnostic


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._selected_path: Path | None = None
        self._diagnostics: list[Diagnostic] = []
        self._filtered_diagnostics: list[Diagnostic] = []
        self._dark_theme = True

        self.setWindowTitle("FixMyMods — анализатор логов Minecraft")
        self.resize(1040, 680)
        self.setMinimumSize(760, 500)
        self.setStyleSheet(self._material_stylesheet())

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(18)

        title = QLabel("FixMyMods")
        title.setObjectName("appTitle")
        root_layout.addWidget(title)

        subtitle = QLabel(
            "Диагностика Minecraft: несовместимые моды, отсутствующие зависимости, Java-ошибки и конфликты загрузчика."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        root_layout.addWidget(subtitle)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(12)

        self.file_label = QLabel("Файл не выбран")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setWordWrap(True)
        self.file_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.open_button = QPushButton("Выбрать лог")
        self.open_button.clicked.connect(self.choose_file)

        self.demo_button = QPushButton("Пример лога")
        self.demo_button.clicked.connect(self.load_demo_log)

        self.analyze_button = QPushButton("Анализировать")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_selected_file)

        self.clear_button = QPushButton("Очистить")
        self.clear_button.clicked.connect(self.clear_results)

        self.theme_button = QPushButton("Светлая тема")
        self.theme_button.clicked.connect(self.toggle_theme)

        controls_row.addWidget(self.file_label, 1)
        controls_row.addWidget(self.open_button)
        controls_row.addWidget(self.demo_button)
        controls_row.addWidget(self.analyze_button)
        controls_row.addWidget(self.clear_button)
        controls_row.addWidget(self.theme_button)
        root_layout.addLayout(controls_row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        self.total_card = self._make_stat_card("Всего", "0")
        self.error_card = self._make_stat_card("Ошибка", "0", accent="#ff6b6b")
        self.warning_card = self._make_stat_card("Внимание", "0", accent="#ffb454")
        self.info_card = self._make_stat_card("Инфо", "0", accent="#6ab7ff")

        for card in (self.total_card, self.error_card, self.warning_card, self.info_card):
            stats_row.addWidget(card)
        root_layout.addLayout(stats_row)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        toolbar.addWidget(QLabel("Фильтр:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все", "Ошибка", "Внимание", "Инфо"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        toolbar.addWidget(self.filter_combo)
        toolbar.addStretch(1)
        root_layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.diagnostics_list = QListWidget()
        self.diagnostics_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.diagnostics_list.currentRowChanged.connect(self.show_diagnostic_details)

        self.details_view = QTextEdit()
        self.details_view.setReadOnly(True)
        self.details_view.setPlaceholderText(
            "Выберите найденную проблему, чтобы увидеть подробности."
        )
        self.details_view.setStyleSheet(
            "QTextEdit { background: #1b2333; color: #edf2ff; border: 1px solid #394868; border-radius: 16px; }"
        )

        splitter.addWidget(self.diagnostics_list)
        splitter.addWidget(self.details_view)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root_layout.addWidget(splitter, 1)

        self.setCentralWidget(central_widget)
        self.statusBar().showMessage("Готов к анализу")
        self._refresh_summary_cards()

    def _material_stylesheet(self) -> str:
        if self._dark_theme:
            return """
            QMainWindow {
                background: #0d1321;
                color: #edf2ff;
            }
            QWidget {
                background-color: #0d1321;
                color: #edf2ff;
            }
            QLabel#appTitle {
                font-size: 30px;
                font-weight: 800;
                color: #f5f7ff;
            }
            QLabel#subtitle {
                color: #b7bfde;
                font-size: 14px;
            }
            QLabel#summaryText {
                color: #edf2ff;
                background-color: #1f2a3d;
                border: 1px solid #3a4d75;
                border-radius: 14px;
                padding: 10px 12px;
            }
            QLabel#fileLabel {
                background-color: #1a2233;
                border: 1px solid #394868;
                border-radius: 12px;
                padding: 10px 12px;
                color: #edf2ff;
            }
            QPushButton {
                background-color: #8a7af5;
                color: #ffffff;
                border: none;
                border-radius: 14px;
                min-height: 40px;
                padding: 0 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #9181f7;
            }
            QPushButton:pressed {
                background-color: #7a6bf0;
            }
            QPushButton:disabled {
                background-color: #3b4258;
                color: #8d94ad;
            }
            QComboBox, QTextEdit, QListWidget {
                background-color: #171f2d;
                border: 1px solid #394868;
                border-radius: 14px;
                color: #edf2ff;
                selection-background-color: #745ef6;
            }
            QTextEdit {
                padding: 14px 16px;
            }
            QListWidget {
                border-radius: 18px;
            }
            QListWidget::item {
                padding: 12px 10px;
                margin: 2px 4px;
                border-radius: 12px;
            }
            QListWidget::item:selected {
                background-color: #413d7a;
                color: #edf2ff;
            }
            QFrame {
                background-color: #171f2d;
                border: 1px solid #2e3b57;
                border-radius: 18px;
            }
            QLabel#statTitle {
                color: #a9b5d8;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            QLabel#statValue {
                font-size: 24px;
                font-weight: 800;
            }
            QSplitter::handle {
                background: #2b3854;
            }
            QStatusBar {
                background: #171f2d;
                color: #edf2ff;
            }
            """

        return """
            QMainWindow {
                background: #f5f7fb;
                color: #1d2433;
            }
            QWidget {
                background-color: #f5f7fb;
                color: #1d2433;
            }
            QLabel#appTitle {
                font-size: 30px;
                font-weight: 800;
                color: #1d2433;
            }
            QLabel#subtitle {
                color: #5e647c;
                font-size: 14px;
            }
            QLabel#summaryText {
                color: #1d2433;
                background-color: #edf3ff;
                border: 1px solid #dfe8ff;
                border-radius: 12px;
                padding: 10px 12px;
            }
            QLabel#fileLabel {
                background-color: #ffffff;
                border: 1px solid #dfe8ff;
                border-radius: 12px;
                padding: 10px 12px;
                color: #1d2433;
            }
            QPushButton {
                background-color: #6750a4;
                color: #ffffff;
                border: none;
                border-radius: 14px;
                min-height: 40px;
                padding: 0 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5d4aa1;
            }
            QPushButton:pressed {
                background-color: #4c3d91;
            }
            QPushButton:disabled {
                background-color: #d7dbe5;
                color: #7c8197;
            }
            QComboBox, QTextEdit, QListWidget {
                background-color: #ffffff;
                border: 1px solid #dfe8ff;
                border-radius: 14px;
                color: #1d2433;
                selection-background-color: #d7c6ff;
            }
            QTextEdit {
                padding: 14px 16px;
            }
            QListWidget {
                border-radius: 18px;
            }
            QListWidget::item {
                padding: 12px 10px;
                margin: 2px 4px;
                border-radius: 12px;
            }
            QListWidget::item:selected {
                background-color: #e7dcff;
                color: #1d2433;
            }
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e6ebff;
                border-radius: 18px;
            }
            QLabel#statTitle {
                color: #626d87;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            QLabel#statValue {
                font-size: 24px;
                font-weight: 800;
            }
            QSplitter::handle {
                background: #dde6ff;
            }
            QStatusBar {
                background: #eef3ff;
                color: #1d2433;
            }
            """

    def _make_stat_card(self, title: str, value: str, accent: str = "#6750a4") -> QFrame:
        frame = QFrame()
        frame.setMinimumHeight(82)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 10, 14, 10)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet(f"color: {accent};")

        frame.value_label = value_label
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return frame

    def choose_file(self) -> None:
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите лог Minecraft",
            "",
            "Логи и отчёты (*.log *.txt);;Все файлы (*)",
        )
        if selected_path:
            self.set_log_file(selected_path)

    def set_log_file(self, path: str | Path) -> None:
        self._selected_path = Path(path)
        self.file_label.setText(str(self._selected_path))
        self.file_label.setToolTip(str(self._selected_path))
        self.analyze_button.setEnabled(True)
        self._diagnostics = []
        self._filtered_diagnostics = []
        self.diagnostics_list.clear()
        self.details_view.clear()
        self._refresh_summary_cards()
        self.statusBar().showMessage("Файл выбран. Нажмите «Анализировать».")

    def clear_results(self) -> None:
        self._selected_path = None
        self._diagnostics = []
        self._filtered_diagnostics = []
        self.file_label.setText("Файл не выбран")
        self.analyze_button.setEnabled(False)
        self.diagnostics_list.clear()
        self.details_view.clear()
        self.filter_combo.setCurrentIndex(0)
        self._refresh_summary_cards()
        self.statusBar().showMessage("Готов к анализу")

    def analyze_selected_file(self) -> None:
        if self._selected_path is None:
            return

        if not self._selected_path.is_file():
            self._show_file_error(
                f"Файл не найден или не является обычным файлом:\n{self._selected_path}"
            )
            return

        try:
            diagnostics = analyze_file(self._selected_path)
        except OSError as error:
            self._show_file_error(
                f"Не удалось прочитать файл:\n{self._selected_path}\n\n{error}"
            )
            return

        self._diagnostics = diagnostics
        self.filter_combo.setCurrentIndex(0)
        self.apply_filter(0)

        if self._filtered_diagnostics:
            self.statusBar().showMessage(
                f"Найдено диагностик: {len(self._filtered_diagnostics)}"
            )
        else:
            self.details_view.setPlainText(
                "Известные проблемы не обнаружены.\n\n"
                "Это не гарантирует, что в логе нет ошибок: FixMyMods пока "
                "распознаёт только часть распространённых сообщений."
            )
            self.statusBar().showMessage("Известные проблемы не обнаружены")

    def apply_filter(self, index: int) -> None:
        filters = ["all", "error", "warning", "info"]
        level = filters[index]

        if not self._diagnostics:
            self._filtered_diagnostics = []
            self.diagnostics_list.clear()
            self._refresh_summary_cards()
            return

        if level == "all":
            self._filtered_diagnostics = list(self._diagnostics)
        else:
            self._filtered_diagnostics = [
                d for d in self._diagnostics if d.severity == level
            ]

        self.diagnostics_list.clear()
        for diagnostic in self._filtered_diagnostics:
            item = QListWidgetItem(
                f"{self._severity_label(diagnostic.severity)} {diagnostic.title}"
            )
            item.setData(Qt.ItemDataRole.UserRole, diagnostic.rule_id)
            self.diagnostics_list.addItem(item)

        if self._filtered_diagnostics:
            self.diagnostics_list.setCurrentRow(0)
        else:
            self.details_view.clear()
        self._refresh_summary_cards()

    def show_diagnostic_details(self, row: int) -> None:
        if row < 0 or row >= len(self._filtered_diagnostics):
            return

        diagnostic = self._filtered_diagnostics[row]
        suggestions = "\n".join(f"• {suggestion}" for suggestion in diagnostic.suggestions)
        evidence = "\n".join(f"  {line}" for line in diagnostic.evidence)
        self.details_view.setPlainText(
            f"{diagnostic.title}\n\n"
            f"Что это значит:\n{diagnostic.description}\n\n"
            f"Что нужно сделать:\n• " + "\n• ".join(diagnostic.suggestions) + "\n\n"
            f"Строки из файла:\n• " + "\n• ".join(diagnostic.evidence)
        )

    def _refresh_summary_cards(self) -> None:
        total = len(self._diagnostics)
        errors = sum(1 for d in self._diagnostics if d.severity == "error")
        warnings = sum(1 for d in self._diagnostics if d.severity == "warning")
        infos = sum(1 for d in self._diagnostics if d.severity == "info")

        self.total_card.value_label.setText(str(total))
        self.error_card.value_label.setText(str(errors))
        self.warning_card.value_label.setText(str(warnings))
        self.info_card.value_label.setText(str(infos))

    @staticmethod
    def _severity_label(severity: str) -> str:
        return {
            "error": "[ОШИБКА]",
            "warning": "[ВНИМАНИЕ]",
            "info": "[ИНФО]",
        }.get(severity, "[ДИАГНОСТИКА]")

    def load_demo_log(self) -> None:
        demo_path = Path(__file__).resolve().parents[2] / "examples" / "sample-crash-report.txt"
        if demo_path.exists():
            self.set_log_file(demo_path)
            self.analyze_selected_file()
        else:
            QMessageBox.warning(self, "Пример не найден", "Файл examples/sample-crash-report.txt не найден.")

    def toggle_theme(self) -> None:
        self._dark_theme = not self._dark_theme
        self.setStyleSheet(self._material_stylesheet())
        self.theme_button.setText("Светлая тема" if self._dark_theme else "Тёмная тема")

    def _show_file_error(self, message: str) -> None:
        self._diagnostics = []
        self._filtered_diagnostics = []
        self.diagnostics_list.clear()
        self.details_view.clear()
        self._refresh_summary_cards()
        self.statusBar().showMessage("Ошибка чтения файла")
        QMessageBox.critical(self, "Ошибка открытия файла", message)
