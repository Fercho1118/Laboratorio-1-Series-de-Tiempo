"""Prepara el entorno: crea el venv en .venv/ e instala requirements.txt."""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VENV = RAIZ / ".venv"
REQUIREMENTS = RAIZ / "requirements.txt"

if sys.platform == "win32":
    PYTHON_VENV = VENV / "Scripts" / "python.exe"
    ACTIVAR = ".venv\\Scripts\\activate"
else:
    PYTHON_VENV = VENV / "bin" / "python"
    ACTIVAR = "source .venv/bin/activate"


def main():
    if not VENV.exists():
        print(f"Creando entorno virtual en {VENV}")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    else:
        print(f"El entorno {VENV} ya existe, se reutiliza")

    print("Instalando dependencias de requirements.txt")
    subprocess.run([str(PYTHON_VENV), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(PYTHON_VENV), "-m", "pip", "install", "-r", str(REQUIREMENTS)], check=True)

    print("\nListo. Activa el entorno con:")
    print(f"  {ACTIVAR}")
    print("y luego corre el pipeline con:")
    print("  python src/run_pipeline.py")


if __name__ == "__main__":
    main()
