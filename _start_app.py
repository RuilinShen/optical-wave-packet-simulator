import subprocess, time, urllib.request
import os, sys

# Kill old streamlit
os.system('taskkill /F /IM "streamlit.exe" 2>nul')
time.sleep(2)

# Start validation server if needed
try:
    urllib.request.urlopen("http://localhost:5000/health", timeout=2)
    print("Validation server: alive")
except:
    subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.join(os.getcwd(), "server"),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    print("Validation server: started")

# Start Streamlit
proc = subprocess.Popen(
    [".venv\\Scripts\\streamlit.exe", "run", "app.py",
     "--server.headless", "true", "--server.port", "8899"],
    cwd=os.getcwd(),
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(10)
try:
    r = urllib.request.urlopen("http://localhost:8899", timeout=5)
    print(f"App: http://localhost:8899 (PID: {proc.pid})")
except Exception as e:
    print(f"Failed: {e}")
