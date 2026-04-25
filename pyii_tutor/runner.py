from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass


@dataclass(frozen=True)
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    timeout: bool = False


def run_code(code: str, timeout_s: float = 2.5) -> RunResult:
    """
    Ejecuta el código en un proceso separado y captura stdout/stderr.
    Nota: esto NO es un sandbox de seguridad; úsalo como recurso educativo local.
    """
    code = code.rstrip() + "\n"
    with tempfile.TemporaryDirectory(prefix="pyii_tutor_") as td:
        script_path = os.path.join(td, "snippet.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            proc = subprocess.run(
                [sys.executable, "-I", script_path],
                cwd=td,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=timeout_s,
            )
            return RunResult(ok=proc.returncode == 0, stdout=proc.stdout, stderr=proc.stderr, timeout=False)
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "") if isinstance(e.stdout, str) else (e.stdout.decode("utf-8", "ignore") if e.stdout else "")
            err = (e.stderr or "") if isinstance(e.stderr, str) else (e.stderr.decode("utf-8", "ignore") if e.stderr else "")
            return RunResult(ok=False, stdout=out, stderr=err or "Tiempo de ejecución excedido.", timeout=True)
