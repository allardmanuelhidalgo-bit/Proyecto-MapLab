# run.py
#
# Levanta el backend (FastAPI/uvicorn) y el frontend (Streamlit) juntos,
# con un solo comando: python run.py
#
# Equivale a correr en dos terminales separadas:
#   uvicorn backend.main:app --reload
#   streamlit run frontend/app.py
#
# Con Ctrl+C se apagan los dos procesos.

import subprocess
import sys
import time

BACKEND_CMD = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"]
FRONTEND_CMD = [sys.executable, "-m", "streamlit", "run", "frontend/app.py"]


def main():
    print("Iniciando backend en http://localhost:8000 (docs en /docs)...")
    backend = subprocess.Popen(BACKEND_CMD)

    # Pequena espera para que el backend arranque antes de abrir el frontend
    time.sleep(2)

    print("Iniciando frontend en http://localhost:8501 ...")
    frontend = subprocess.Popen(FRONTEND_CMD)

    try:
        # Espera a que cualquiera de los dos procesos termine
        while True:
            if backend.poll() is not None:
                print("El backend se detuvo.")
                break
            if frontend.poll() is not None:
                print("El frontend se detuvo.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo backend y frontend...")
    finally:
        for proceso in (backend, frontend):
            if proceso.poll() is None:
                proceso.terminate()
        for proceso in (backend, frontend):
            try:
                proceso.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proceso.kill()


if __name__ == "__main__":
    main()