# scripts/diagnose.py
"""
Знаходить у проєкті все, що стосується Vireo wire/crypto.
Запуск: python scripts/diagnose.py
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Що шукаємо в іменах функцій/класів/констант
TARGETS = {
    "canonical", "wire_hash", "payload_hash", "did_hash",
    "sign_vireo", "verify_vireo", "blake2",
    "canonical_wire_bytes", "parse_wire_bytes",
    "WIRE_MAGIC", "WIRE_VERSION", "HEADER_SIZE",
    "Envelope", "Keypair", "Agent",
    "intent_to_id", "id_to_intent",
    "jcs", "canonicalize",
}

# Що шукаємо в рядках (щоб зловити навіть динамічні виклики)
TEXT_HINTS = [
    "VIRE", "0x0301", "did:vireo:", "blake2b",
    "PROPOSE", "NEGOTIATE", "EXECUTE",
]


def scan_python(path: Path):
    """Парсить .py і повертає знайдені імена верхнього рівня."""
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return None, f"read error: {e}"

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return None, f"syntax error: {e}"

    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.lower() in TARGETS or any(t in node.name.lower() for t in TARGETS):
                found.append(f"def {node.name}")
        elif isinstance(node, ast.ClassDef):
            if node.name in TARGETS:
                found.append(f"class {node.name}")
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in TARGETS:
                    found.append(f"const {t.id}")

    # текстові хінти
    hints = [h for h in TEXT_HINTS if h in src]
    return {"symbols": found, "hints": hints}, None


def main():
    print(f"ROOT = {ROOT}\n")

    py_files = sorted(ROOT.rglob("*.py"))
    print(f"=== Python files: {len(py_files)} ===\n")

    hits = []
    for f in py_files:
        # пропускаємо venv / .git / node_modules
        parts = set(f.parts)
        if parts & {"venv", ".venv", "env", ".git", "node_modules", "__pycache__"}:
            continue

        result, err = scan_python(f)
        rel = f.relative_to(ROOT)
        if err:
            print(f"  ⚠️  {rel}: {err}")
            continue
        if result["symbols"] or result["hints"]:
            hits.append((rel, result))

    print(f"\n=== Files with Vireo symbols/hints: {len(hits)} ===\n")
    for rel, res in hits:
        print(f"📄 {rel}")
        for s in res["symbols"]:
            print(f"     • {s}")
        if res["hints"]:
            print(f"     hints: {', '.join(res['hints'])}")
        print()

    # JSON vectors
    print("=== JSON vectors ===")
    vec = ROOT / "tests" / "conformance" / "vectors"
    if vec.exists():
        for j in sorted(vec.glob("*.json")):
            size = j.stat().st_size
            print(f"  {j.relative_to(ROOT)}  ({size} bytes)")
            if size < 4000:
                print("  ---")
                print(j.read_text(encoding="utf-8"))
                print("  ---")
    else:
        print(f"  ❌ {vec} не існує")


if __name__ == "__main__":
    main()