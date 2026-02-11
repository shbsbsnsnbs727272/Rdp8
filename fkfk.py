import subprocess
import time
import os

# --- Configuration ---
# If scrcpy is in your system's PATH, just use "scrcpy".
# Otherwise, provide the full path to the executable, e.g., r"C:\path\to\scrcpy\scrcpy.exe"
SCRCPY_EXECUTABLE = "scrcpy" 

def run_scrcpy_usb():
    print(f"Attempting to launch {SCRCPY_EXECUTABLE} for USB connected device...")
    print("Ensure your Android device is connected via USB and USB debugging is enabled.")
    
    try:
        # Launch scrcpy process. It will automatically detect a single connected USB device.
        # The process will run in the background until the script is terminated or the scrcpy window is closed.
        process = subprocess.Popen([SCRCPY_EXECUTABLE])
        print("Scrcpy running. Press Ctrl+C in this Python console to stop mirroring.")
        
        # Keep the script alive while scrcpy runs
        process.wait() 
        
    except FileNotFoundError:
        print(f"Error: {SCRCPY_EXECUTABLE} not found.")
        print("Please check your SCRCPY_EXECUTABLE path or ensure it is added to your system's PATH environment variables.")
    except KeyboardInterrupt:
        print("Scrcpy process terminated by user (Ctrl+C).")
        if process and process.poll() is None:
            process.terminate()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_scrcpy_usb()
