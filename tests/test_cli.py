"""
tests/test_cli.py
-----------------
Tests del lanzador raíz `tie.py`.
"""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_root_cli_fibonacci():
    """CLI raíz: ejecuta un ejemplo real y termina con código 0."""
    print("── CLI: tie.py fibonacci.tie ────────────")
    proc = subprocess.run(
        [sys.executable, "tie.py", "examples/fibonacci.tie"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    ok = (
        proc.returncode == 0
        and "Salida:  [0, 1, 1, 2, 3, 5, 8, 13]" in proc.stdout
    )
    print(f"  Return code: {proc.returncode}")
    print(f"  {'✅' if ok else '❌'}")
    assert ok
    print()


if __name__ == "__main__":
    print("=" * 45)
    print("  TIE-Lang — Tests: CLI")
    print("=" * 45)
    print()
    test_root_cli_fibonacci()
    print("✅ CLI raíz verificado")
