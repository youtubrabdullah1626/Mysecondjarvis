"""Camera manager for Jarvis - handles camera initialization and access"""
import cv2
import numpy as np
import os
import json
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
import threading
import atexit
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from features.storage import data_path, ensure_data_dir

class CameraManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CameraManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the camera manager"""
        self.cap = None
        self.current_camera_index = -1
        self.last_frame = None
        self.last_frame_time = 0
        self.camera_properties = {}
        self.is_running = False
        self.background_thread = None
        # Do NOT start background capture automatically. Call start(owner) to begin capturing.
        self.owner = None
        atexit.register(self.cleanup)
        
    def _start_background_capture(self):
        """Start background thread for continuous camera capture"""
        if self.background_thread is not None:
            return
        self.is_running = True
        self.background_thread = threading.Thread(target=self._background_capture_task)
        self.background_thread.daemon = True
        self.background_thread.start()

    def start(self, owner: str = 'default') -> Tuple[bool, str]:
        """Start background capture if no other owner is active. Returns (ok, message)."""
        if self.owner and self.owner != owner:
            return False, f"Camera already owned by {self.owner}"
        if self.background_thread is None or not self.background_thread.is_alive():
            self.owner = owner
            self._start_background_capture()
            return True, f"Camera started by {owner}"
        self.owner = owner
        return True, "Camera already running"

    def stop(self, owner: str = 'default') -> Tuple[bool, str]:
        """Stop background capture if called by owner. Returns (ok, message)."""
        if self.owner and self.owner != owner:
            return False, f"Cannot stop camera owned by {self.owner}"
        self.owner = None
        self.is_running = False
        if self.background_thread is not None:
            self.background_thread.join(timeout=1.0)
            self.background_thread = None
        return True, "Camera stopped"
    
    def _background_capture_task(self):
        """Background task to continuously capture frames"""
        while self.is_running:
            try:
                if self.cap is None or not self.cap.isOpened():
                    print("Trying to initialize camera...")
                    if not self._initialize_camera():
                        print("Failed to initialize camera, retrying in 2 seconds...")
                        with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                            f.write("Camera initialization in progress...")
                        time.sleep(2)
                        continue

                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print("Failed to read frame, reinitializing camera...")
                    self._initialize_camera()
                    continue

                # Check if frame is empty or all black
                if frame.size == 0 or np.mean(frame) < 5:
                    print("Invalid frame detected (empty or black), reinitializing...")
                    self._initialize_camera()
                    continue

                self.last_frame = frame.copy()
                self.last_frame_time = time.time()
                self._process_frame(frame)
                
            except Exception as e:
                print(f"Camera error: {str(e)}")
                with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                    f.write("Camera error occurred, trying to recover...")
                time.sleep(2)
                
    def _initialize_camera(self) -> bool:
        """Initialize the camera, trying multiple indices and backends"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        # Try a list of indices and backends. We'll attempt:
        #  - Windows-specific backends (DSHOW, MSMF)
        #  - Open with no backend (let OpenCV choose)
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]
        indices = list(range(4))  # try 0..3

        last_error = None
        for idx in indices:
            for backend in backends:
                try:
                    if backend is None:
                        print(f"Trying camera index {idx} with default backend...")
                        cap = cv2.VideoCapture(idx)
                    else:
                        print(f"Trying camera index {idx} with backend {backend}...")
                        cap = cv2.VideoCapture(idx, backend)

                    if not cap or not cap.isOpened():
                        print(f"Failed to open camera {idx} with backend {backend}")
                        try:
                            cap.release()
                        except Exception:
                            pass
                        continue

                    # Warm up and read a frame
                    time.sleep(0.2)
                    ret, frame = cap.read()
                    if not ret or frame is None or frame.size == 0:
                        print(f"Camera {idx} opened but failed to return a valid frame")
                        try:
                            cap.release()
                        except Exception:
                            pass
                        continue

                    # Good frame — set preferred properties
                    try:
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                    except Exception:
                        pass

                    # Verify subsequent frames are valid
                    valid = True
                    for _ in range(2):
                        ret, tmp = cap.read()
                        if not ret or tmp is None or tmp.size == 0:
                            valid = False
                            break
                        if np.mean(tmp) < 1:
                            valid = False
                            break

                    if not valid:
                        print(f"Camera {idx} produced invalid frames after init")
                        try:
                            cap.release()
                        except Exception:
                            pass
                        continue

                    # Camera works
                    self.cap = cap
                    self.current_camera_index = idx
                    self.camera_properties = {
                        'index': idx,
                        'backend': backend,
                        'width': cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                        'height': cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                        'fps': cap.get(cv2.CAP_PROP_FPS),
                    }
                    print(f"Successfully initialized camera {idx} with backend {backend}")
                    try:
                        with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                            f.write('Camera initialized successfully')
                    except Exception:
                        pass
                    return True

                except Exception as e:
                    last_error = e
                    print(f"Error trying camera {idx} with backend {backend}: {str(e)}")
                    try:
                        if 'cap' in locals() and cap is not None:
                            cap.release()
                    except Exception:
                        pass
                    continue

        # No camera succeeded
        print("Failed to initialize any camera")
        try:
            with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                f.write('No camera available or failed to initialize')
        except Exception:
            pass
        if last_error:
            print(f"Last error: {str(last_error)}")
        return False
        
    def _process_frame(self, frame):
        """Process the captured frame and update camera_view.txt"""
        try:
            # Basic frame validation
            if frame is None or frame.size == 0:
                raise ValueError("Invalid frame")

            # Check if frame is too dark or too bright
            average_brightness = np.mean(frame)
            if average_brightness < 30:
                description = "Camera me kuch clear nahi dikh raha hai, bahut andhera hai."
            elif average_brightness > 240:
                description = "Camera me kuch clear nahi dikh raha hai, bahut roshni hai."
            else:
                # Convert to grayscale for processing
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Try to detect faces
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                # Look for movement/changes in the frame
                if hasattr(self, 'last_gray'):
                    frame_delta = cv2.absdiff(self.last_gray, gray)
                    movement = np.mean(frame_delta) > 10
                else:
                    movement = False
                self.last_gray = gray
                
                # Create detailed description
                num_faces = len(faces)
                if num_faces > 0:
                    description = f"Camera me {num_faces} person dikh {'rahe hain' if num_faces != 1 else 'raha hai'}"
                    if movement:
                        description += " aur movement ho rahi hai."
                    else:
                        description += " aur koi movement nahi ho rahi hai."
                else:
                    if movement:
                        description = "Camera me koi person nahi dikh raha hai, lekin kuch movement ho rahi hai."
                    else:
                        description = "Camera me koi person nahi dikh raha hai aur koi movement bhi nahi hai."
            
            # Save description
            with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                f.write(description)
                
        except Exception as e:
            print(f"Camera processing error: {str(e)}")
            try:
                with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                    f.write("Camera processing me error aa raha hai, dubara koshish kar raha hun...")
            except Exception as e2:
                print(f"Failed to write camera_view.txt: {str(e2)}")
                
    def get_latest_frame(self) -> Tuple[bool, Optional[Any]]:
        """Get the most recent frame"""
        if self.last_frame is None:
            return False, None
        if time.time() - self.last_frame_time > 5:  # Frame is too old
            return False, None
        return True, self.last_frame.copy()
            
    def cleanup(self):
        """Cleanup resources"""
        self.is_running = False
        if self.background_thread is not None:
            self.background_thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
    def release(self):
        """Safely release the camera"""
        self.cleanup()
            
    def get_camera_status(self) -> Dict[str, Any]:
        """Get current camera status"""
        return {
            'initialized': self.cap is not None and self.cap.isOpened(),
            'camera_index': self.current_camera_index,
            'last_frame_time': self.last_frame_time,
            'properties': self.camera_properties
        }

    # Public wrapper for external callers/tests
    def initialize_camera(self, owner: Optional[str] = None) -> Tuple[bool, str]:
        """Public wrapper to initialize the camera. Requires owner (e.g. 'gui').
        Returns (success, message). If owner is None, initialization is refused to
        enforce GUI-only access by default.
        """
        if owner is None:
            return False, "Camera initialization disabled: must be started by GUI (provide owner)"
        # If owner provided, ensure ownership and start
        if self.owner and self.owner != owner:
            return False, f"Camera already owned by {self.owner}"
        # start background capture under owner
        ok, msg = self.start(owner=owner)
        if not ok:
            return False, msg
        return True, f"Camera initialized by {owner}"

    def read_frame(self, owner: Optional[str] = None) -> Tuple[bool, Optional[np.ndarray]]:
        """Public method to read a fresh frame from the camera. Returns (ret, frame).
        If the camera is not owned, reading is refused to ensure only GUI owner reads.
        If owner is provided it must match current owner.
        """
        try:
            # Enforce ownership: camera must be started and owner must match (if provided)
            if self.owner is None:
                return False, None
            if owner is not None and owner != self.owner:
                return False, None

            if self.cap is None or not self.cap.isOpened():
                # If camera is supposed to be running, try initialize internally
                if not self._initialize_camera():
                    return False, None

            ret, frame = self.cap.read()
            if not ret or frame is None or frame.size == 0:
                # try a reinit once
                if self._initialize_camera():
                    ret, frame = self.cap.read()
                else:
                    return False, None
            return ret, frame
        except Exception as e:
            print(f"read_frame error: {str(e)}")
            return False, None

# Global camera manager instance
camera = CameraManager()

if __name__ == "__main__":
    try:
        # Add the parent directory to Python path
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        print("Testing camera manager...")
        print("Current status:", camera.get_camera_status())
        
        # Try to read some frames
        for i in range(5):
            ret, frame = camera.get_latest_frame()
            if ret:
                print(f"Successfully read frame {i+1}")
                print(f"Frame shape: {frame.shape}")
                print(f"Average brightness: {np.mean(frame):.2f}")
            else:
                print(f"Failed to read frame {i+1}")
            time.sleep(1)
            
        print("\nFinal camera status:", camera.get_camera_status())
        print("\nTest complete. Check camera_view.jpg and camera_view.txt in the data directory.")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
    finally:
        camera.cleanup()