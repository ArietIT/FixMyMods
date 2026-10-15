import re
from collections.abc import Iterable, Sequence
from typing import Protocol

from .models import Diagnostic

SUPPORTED_PROBLEM_TYPES = (
    "Incompatible mods found!",
    "Missing mod dependency",
    "Missing Java class",
    "Unsupported Java version",
    "Out of memory / Java heap issue",
    "Duplicate class / duplicate mod",
    "Missing native library",
    "Mod loader / method mismatch",
    "Crash with main class / launch failure",
    "Mixin / transformer conflict",
)


class DiagnosticRule(Protocol):
    def analyze(self, lines: Sequence[str]) -> list[Diagnostic]:
        ...


class PatternBasedRule:
    rule_id = ""
    title = ""
    description = ""
    severity = "error"
    suggestions: tuple[str, ...] = ()
    pattern = re.compile(r".")

    def analyze(self, lines: Sequence[str]) -> list[Diagnostic]:
        evidence = tuple(line for line in lines if self.pattern.search(line))
        if not evidence:
            return []
        return [
            Diagnostic(
                rule_id=self.rule_id,
                title=self.title,
                description=self.description,
                severity=self.severity,
                suggestions=self.suggestions,
                evidence=evidence,
            )
        ]


class IncompatibleModsRule(PatternBasedRule):
    rule_id = "incompatible-mods"
    title = "Обнаружены несовместимые моды"
    description = (
        "Загрузчик модов сообщает, что некоторые установленные "
        "моды несовместимы друг с другом или с этой версией игры."
    )
    severity = "error"
    suggestions = (
        "Найдите подробности о конфликте в логе или crash-report.",
        "Убедитесь, что версии модов подходят для вашей версии Minecraft и загрузчика.",
        "Обновите, удалите или замените моды, указанные в отчёте.",
    )
    pattern = re.compile(r"\bincompatible mods found!?\b", re.IGNORECASE)


class MissingDependencyRule(PatternBasedRule):
    rule_id = "missing-dependency"
    title = "Не найдена зависимость мода"
    description = (
        "Загрузчик модов сообщает, что установленному моду "
        "требуется другой мод, которого нет."
    )
    severity = "error"
    suggestions = (
        "Посмотрите в логе или crash-report название требуемого мода.",
        "Установите его версию, совместимую с вашей версией Minecraft и загрузчика.",
        "Если мод, которому нужна зависимость, не требуется, удалите его.",
    )
    pattern = re.compile(r"\brequires\b.*\bwhich\s+is\s+missing\b", re.IGNORECASE)


class MissingJavaClassRule(PatternBasedRule):
    rule_id = "missing-java-class"
    title = "Отсутствует Java-класс"
    description = (
        "Запуск Minecraft упёрся в отсутствующий класс или зависимость Java. "
        "Это обычно означает, что мод, библиотека или версия Java установлены неправильно."
    )
    severity = "error"
    suggestions = (
        "Проверьте, нет ли в логе имени класса, которого не хватает.",
        "Обновите Java до версии, поддерживаемой вашим набором модов.",
        "Переустановите или обновите мод, который пытается загрузить этот класс.",
    )
    pattern = re.compile(
        r"(?:ClassNotFoundException|NoClassDefFoundError|java\.lang\.(?:ClassNotFoundException|NoClassDefFoundError))",
        re.IGNORECASE,
    )


class UnsupportedJavaVersionRule(PatternBasedRule):
    rule_id = "unsupported-java-version"
    title = "Неподдерживаемая версия Java"
    description = (
        "Minecraft или мод пытаются запуститься на неподдерживаемой версии Java. "
        "Многие модпаки требуют Java 17 или более новую."
    )
    severity = "warning"
    suggestions = (
        "Проверьте, какая версия Java указана в лаунчере или в логах.",
        "Установите совместимую версию Java (обычно 17+ для новых сборок).",
        "Проверьте, что у вас не смешаны Java 8 и Java 17/21 в одной установке.",
    )
    pattern = re.compile(
        r"(?:UnsupportedClassVersionError|unsupported major\.minor version|requires Java \d+|java version .* is not supported|Unsupported class file major version)",
        re.IGNORECASE,
    )


class OutOfMemoryRule(PatternBasedRule):
    rule_id = "out-of-memory"
    title = "Ошибка нехватки памяти"
    description = (
        "Игра или моды исчерпали память Java. Это часто связано с большими модпаками, "
        "видеодрайверами или неправильными настройками выделения RAM."
    )
    severity = "warning"
    suggestions = (
        "Увеличьте выделенную память в лаунчере или настройках запуска.",
        "Уберите слишком тяжёлые моды или уменьшите их количество.",
        "Проверьте, не запущены ли лишние программы, поглощающие память.",
    )
    pattern = re.compile(
        r"(?:OutOfMemoryError|Java heap space|GC overhead limit exceeded|not enough memory)",
        re.IGNORECASE,
    )


class DuplicateClassRule(PatternBasedRule):
    rule_id = "duplicate-class"
    title = "Дублирующийся класс или конфликт модов"
    description = (
        "Лог показывает дублирующиеся классы или конфликт между несколькими версиями "
        "одного и того же мода или библиотеки."
    )
    severity = "error"
    suggestions = (
        "Проверьте, нет ли у вас двух версий одного и того же мода.",
        "Удалите неиспользуемые копии jar-файлов или старые сборки модов.",
        "Переустановите пакет модов, чтобы собрать чистую совместимую комбинацию.",
    )
    pattern = re.compile(
        r"(?:duplicate class|duplicate classes|duplicate.*mod|multiple versions of .* were found|duplicated class)",
        re.IGNORECASE,
    )


class MissingNativeLibraryRule(PatternBasedRule):
    rule_id = "missing-native-library"
    title = "Отсутствует нативная библиотека"
    description = (
        "Minecraft пытается загрузить системную или нативную библиотеку, которой нет "
        "в установке Java или в папке модов. Это часто связано с неправильной Java, "
        "неполной установкой или конфликтом библиотек."
    )
    severity = "error"
    suggestions = (
        "Проверьте имя отсутствующей библиотеки в логе и убедитесь, что она действительно установлена.",
        "Обновите Java и переустановите компоненты, связанные с нативными библиотеками.",
        "Проверьте, не конфликтуют ли моды и не установлены ли лишние версии библиотек.",
    )
    pattern = re.compile(
        r"(?:UnsatisfiedLinkError|failed to load native library|native library .* not found|could not load .*library)",
        re.IGNORECASE,
    )


class MethodMismatchRule(PatternBasedRule):
    rule_id = "method-mismatch"
    title = "Несовместимость методов или загрузчика"
    description = (
        "Лог указывает на конфликт между версиями библиотек, методов или модов, что часто "
        "возникает при смешении несовместимых сборок и модов."
    )
    severity = "error"
    suggestions = (
        "Сверьте версии модов и загрузчика с версией Minecraft.",
        "Проверьте, нет ли у вас старых jar-файлов в папке mods.",
        "Попробуйте чистую установку набора модов или обновить устаревший модпак.",
    )
    pattern = re.compile(
        r"(?:NoSuchMethodError|AbstractMethodError|NoSuchFieldError|IncompatibleClassChangeError|java\.lang\.(?:NoSuchMethodError|AbstractMethodError|NoSuchFieldError|IncompatibleClassChangeError))",
        re.IGNORECASE,
    )


class MainClassLoadErrorRule(PatternBasedRule):
    rule_id = "main-class-load-error"
    title = "Не удалось найти или загрузить главный класс"
    description = (
        "Лаунчер или Java не может найти точку входа запуска Minecraft или модового загрузчика. "
        "Это часто означает ошибку в установке Java, исполняемого файла или конфликт между версиями."
    )
    severity = "error"
    suggestions = (
        "Проверьте, что у вас запущена поддерживаемая версия Java для выбранной сборки.",
        "Переустановите лаунчер или проверьте, не сломан ли исполняемый файл игры.",
        "Удалите лишние старые версии Java и убедитесь, что Minecraft запускается через нужный JDK/JRE.",
    )
    pattern = re.compile(
        r"(?:Could not find or load main class|Error: Unable to load main class|main class .* could not be found)",
        re.IGNORECASE,
    )


class MixinConflictRule(PatternBasedRule):
    rule_id = "mixin-conflict"
    title = "Конфликт mixin / transformer"
    description = (
        "Лог показывает проблему во время преобразования кода модов. Такой сбой обычно возникает "
        "при несовместимых модах, устаревших сборках или конфликте между библиотеками."
    )
    severity = "error"
    suggestions = (
        "Проверьте, нет ли у вас несовместимых модов, изменяющих один и тот же код.",
        "Попробуйте удалить недавно установленный мод и запустить игру заново.",
        "Обновите Fabric/Forge/NeoForge и все зависимости до совместимых версий.",
    )
    pattern = re.compile(
        r"(?:Mixin .* failed|Mixin transformation failed|Mixin apply failed|Mixin error|Mixin .* exception)",
        re.IGNORECASE,
    )


DEFAULT_RULES: tuple[DiagnosticRule, ...] = (
    IncompatibleModsRule(),
    MissingDependencyRule(),
    MissingJavaClassRule(),
    UnsupportedJavaVersionRule(),
    OutOfMemoryRule(),
    DuplicateClassRule(),
    MissingNativeLibraryRule(),
    MethodMismatchRule(),
    MainClassLoadErrorRule(),
    MixinConflictRule(),
)


def analyze_lines(
    lines: Iterable[str],
    rules: Sequence[DiagnosticRule] = DEFAULT_RULES,
) -> list[Diagnostic]:
    log_lines = tuple(lines)
    diagnostics: list[Diagnostic] = []
    for rule in rules:
        diagnostics.extend(rule.analyze(log_lines))
    return diagnostics
