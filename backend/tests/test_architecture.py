import ast
from pathlib import Path

HEALTH_OS_ROOT = Path(__file__).resolve().parents[1] / "health_os"


def test_domain_does_not_import_django() -> None:
    violations = _imports_matching(_layer_files("domain"), {"django"})

    assert violations == []


def test_domain_does_not_import_drf() -> None:
    violations = _imports_matching(
        _layer_files("domain"),
        {"drf_spectacular", "rest_framework"},
    )

    assert violations == []


def test_application_does_not_import_presentation() -> None:
    violations = _imports_containing(_layer_files("application"), "presentation")

    assert violations == []


def test_application_does_not_depend_on_infrastructure() -> None:
    violations = _imports_containing(_layer_files("application"), "infrastructure")

    assert violations == []


def _layer_files(layer_name: str) -> list[Path]:
    return [
        source_file
        for layer_path in HEALTH_OS_ROOT.rglob(layer_name)
        if layer_path.is_dir() and not _is_test_path(layer_path)
        for source_file in layer_path.rglob("*.py")
        if not _is_test_path(source_file)
    ]


def _imports_matching(source_files: list[Path], forbidden_roots: set[str]) -> list[str]:
    violations: list[str] = []

    for source_file in source_files:
        for imported_module in _imported_modules(source_file):
            if _root_module(imported_module) in forbidden_roots:
                violations.append(_format_violation(source_file, imported_module))

    return violations


def _imports_containing(source_files: list[Path], forbidden_part: str) -> list[str]:
    violations: list[str] = []

    for source_file in source_files:
        for imported_module in _imported_modules(source_file):
            if forbidden_part in imported_module.split("."):
                violations.append(_format_violation(source_file, imported_module))

    return violations


def _imported_modules(source_file: Path) -> set[str]:
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(_import_from_module(source_file, node))

    return imported_modules


def _import_from_module(source_file: Path, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""

    package_parts = _package_parts(source_file)
    relative_base = package_parts[: len(package_parts) - node.level + 1]

    if node.module:
        relative_base.extend(node.module.split("."))

    return ".".join(relative_base)


def _package_parts(source_file: Path) -> list[str]:
    relative_path = source_file.relative_to(HEALTH_OS_ROOT.parent)
    return list(relative_path.with_suffix("").parts[:-1])


def _root_module(imported_module: str) -> str:
    return imported_module.split(".", maxsplit=1)[0]


def _format_violation(source_file: Path, imported_module: str) -> str:
    relative_source = source_file.relative_to(HEALTH_OS_ROOT.parent)
    return f"{relative_source}: imports {imported_module}"


def _is_test_path(path: Path) -> bool:
    return "tests" in path.parts or path.name.startswith("test_")
