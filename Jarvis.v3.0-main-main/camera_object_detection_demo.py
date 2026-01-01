import cv2
import numpy as np
import time
import os
import json
from datetime import datetime
from features.storage import data_path, ensure_data_dir
from features.camera_manager import camera  # Import the camera manager

# File to store camera observations
CAMERA_MEMORY_FILE = data_path('camera_observations.json')

def load_camera_memory():
    """Load previous camera observations"""
    if os.path.exists(CAMERA_MEMORY_FILE):
        try:
            with open(CAMERA_MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_camera_observation(observation):
    """Save a new camera observation"""
    observations = load_camera_memory()
    observation['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    observations.append(observation)
    # Keep only last 100 observations to manage file size
    observations = observations[-100:]
    with open(CAMERA_MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(observations, f, ensure_ascii=False, indent=2)
    
    # Also update the camera view text file for immediate access
    with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
        f.write(observation['description'])

def check_camera_properties(cap):
    """Check and print camera properties for debugging"""
    properties = {
        'Frame Width': cap.get(cv2.CAP_PROP_FRAME_WIDTH),
        'Frame Height': cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
        'FPS': cap.get(cv2.CAP_PROP_FPS),
        'Brightness': cap.get(cv2.CAP_PROP_BRIGHTNESS),
        'Contrast': cap.get(cv2.CAP_PROP_CONTRAST),
        'Auto Exposure': cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)
    }
    print("\nCamera Properties:")
    for prop, value in properties.items():
        print(f"{prop}: {value}")
    return properties

# For demo, use Haar cascade for face detection
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
if not os.path.exists(cascade_path):
    print(f"Error: Cannot find face cascade file at {cascade_path}")
    exit()

face_cascade = cv2.CascadeClassifier(cascade_path)
if face_cascade.empty():
    print("Error: Failed to load face cascade classifier")
    exit()

# Initialize the camera using the camera manager, but don't steal from GUI
ok, msg = camera.start(owner='demo')
if not ok:
    print("\nError: Could not start camera for demo.")
    print(msg)
    print("\nIf the GUI is running it owns the camera. Close GUI or run demo with GUI stopped.")
    exit()

print("\nCamera initialized successfully!")
print("Camera properties:", camera.get_camera_status())

frame_count = 0
start_time = time.time()
last_save_time = time.time()  # For tracking when to save observations

# Load previous observations
previous_observations = load_camera_memory()
if previous_observations:
    print("\nLast camera observation:", previous_observations[-1]['description'])
    print("Time:", previous_observations[-1]['timestamp'])

try:
    while True:
        ret, frame = camera.read_frame(owner='demo')
        if not ret or frame is None:
            print("Error: Failed to grab frame. Attempting to recover...")
            time.sleep(1)  # Wait a bit before retrying
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Create observation
        num_faces = len(faces)
        observation = {
            'num_faces': num_faces,
            'description': f"Camera me {num_faces} person dikh {'rahe hain' if num_faces != 1 else 'raha hai'}."
        }
        
        # Draw faces and save observation
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
        
        # Save observation every 5 seconds
        current_time = time.time()
        if current_time - last_save_time >= 5:
            save_camera_observation(observation)
            last_save_time = current_time
        
        # Show frame
        cv2.imshow('Camera - Press Q to exit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Save final observation before exiting
            save_camera_observation(observation)
            break

finally:
    # Release demo ownership
    try:
        camera.stop(owner='demo')
    except Exception:
        pass
    # Close any windows
    cv2.destroyAllWindows()
cv2.destroyAllWindows()
