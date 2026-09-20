import subprocess
import sys
import os
import time

# Launch Isaac Sim as a subprocess with the working flags
isaac_process = subprocess.Popen([
    'isaacsim',
    '--no-window',
    '--/rtx/sceneDb/tlasMemoryFraction=0.3',
], env={
    **os.environ,
    'FASTRTPS_DEFAULT_PROFILES_FILE': os.path.expanduser('~/.ros/fastdds.xml'),
})

print(f"Isaac Sim PID: {isaac_process.pid}")
print("Waiting for Isaac Sim to start...")
time.sleep(30)

# Check if process is still running
if isaac_process.poll() is None:
    print("Isaac Sim is running!")
    print("Check topics: ros2 topic list")
    try:
        isaac_process.wait()
    except KeyboardInterrupt:
        isaac_process.terminate()
else:
    print(f"Isaac Sim exited with code: {isaac_process.returncode}")
