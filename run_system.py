"""
Simple script to run both backend and frontend
"""
import subprocess
import sys
import os
import time
import webbrowser

def main():
    print("=" * 60)
    print("Starting RegRadar System")
    print("=" * 60)
    print()

    # Check .env exists
    if not os.path.exists('.env'):
        print("ERROR: .env file not found!")
        print("Please copy .env.example to .env and configure it")
        input("Press Enter to exit...")
        sys.exit(1)

    print("[1/3] Starting Backend API...")
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]

    backend = subprocess.Popen(
        backend_cmd,
        cwd="backend",
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("      Backend started in new window (PID: {})".format(backend.pid))

    print()
    print("[2/3] Waiting for backend to initialize...")
    time.sleep(5)

    print()
    print("[3/3] Starting Frontend...")
    frontend_cmd = ["npm", "run", "dev"]

    frontend = subprocess.Popen(
        frontend_cmd,
        cwd="frontend",
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("      Frontend started in new window (PID: {})".format(frontend.pid))

    print()
    print("=" * 60)
    print("RegRadar is starting!")
    print("=" * 60)
    print()
    print("Backend API:  http://localhost:8000")
    print("API Docs:     http://localhost:8000/docs")
    print("Frontend UI:  http://localhost:3000")
    print()
    print("Two console windows have opened:")
    print("  1. Backend (FastAPI) - Keep it running")
    print("  2. Frontend (React) - Keep it running")
    print()
    print("=" * 60)

    print()
    print("Opening browser in 3 seconds...")
    time.sleep(3)

    try:
        webbrowser.open('http://localhost:3000')
        print("Browser opened!")
    except:
        print("Please open http://localhost:3000 in your browser manually")

    print()
    print("=" * 60)
    print("System is running!")
    print("=" * 60)
    print()
    print("To stop the servers:")
    print("  - Close the Backend and Frontend console windows")
    print("  - Or press CTRL+C in each window")
    print()
    input("Press Enter to keep this window open (servers will keep running)...")

if __name__ == "__main__":
    main()
