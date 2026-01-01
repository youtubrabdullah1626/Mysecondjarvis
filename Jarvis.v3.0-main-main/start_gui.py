import os
import sys
import signal
from multiprocessing import Process, freeze_support

def run_gui():
    # Import and run GUI in a separate process
    from jarvis_gui import main
    main()

if __name__ == '__main__':
    freeze_support()  # Required for Windows
    
    # Clean up any existing lock files
    try:
        if os.path.exists("jarvis_data/gui_running.lock"):
            os.remove("jarvis_data/gui_running.lock")
    except Exception:
        pass

    # Create data directory if needed
    os.makedirs("jarvis_data", exist_ok=True)
    
    # Start GUI process
    gui_process = Process(target=run_gui)
    gui_process.daemon = False  # Keep running even if parent exits
    gui_process.start()
    
    # Write PID to lock file
    try:
        with open("jarvis_data/gui_running.lock", "w") as f:
            f.write(str(gui_process.pid))
    except Exception:
        pass
    
    # Define cleanup handler
    def cleanup(signum, frame):
        try:
            if os.path.exists("jarvis_data/gui_running.lock"):
                os.remove("jarvis_data/gui_running.lock")
        except Exception:
            pass
        sys.exit(0)
    
    # Register cleanup handler
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    
    # Wait for GUI process
    gui_process.join()