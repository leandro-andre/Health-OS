import ast
from pathlib import Path

IDENTITY_ROOT = Path(__file__).resolve().parents[2]


def test_presentation_can_depend_on_application_and_infrastructure() -> None:
    imports = _imported_modules(IDENTITY_ROOT / "presentation" / "composition.py")

    assert "health_os.modules.identity.application" in imports
    assert "health_os.modules.identity.infrastructure" in imports


def test_application_does_not_depend_on_presentation() -> None:
    violations = [
        str(source_file.relative_to(IDENTITY_ROOT.parent.parent.parent))
        for source_file in (IDENTITY_ROOT / "application").rglob("*.py")
        if "tests" not in source_file.parts
        for imported_module in _imported_modules(source_file)
        if "presentation" in imported_module.split(".")
    ]

    assert violations == []


def _imported_modules(source_file: Path) -> set[str]:
    tree = ast.parse(source_file.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")

    return imported_modules
