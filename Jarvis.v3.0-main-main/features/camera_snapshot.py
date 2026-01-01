"""Camera snapshot functionality for Jarvis"""
import numpy as np
import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from features.camera_manager import camera
from features.storage import data_path

# Do not import cv2 at module import time to avoid loading native libs into
# processes that only import this module (like the agent). Import cv2 lazily
# inside functions that actually use it.
cv2 = None
face_cascade = None

# Load COCO class names
COCO_NAMES = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
              'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
              'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
              'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
              'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
              'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
              'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
              'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
              'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
              'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

async def take_snapshot():
    """Get the latest camera view description"""
    try:
        global cv2, face_cascade
        if cv2 is None:
            try:
                import cv2 as _cv2
                cv2 = _cv2
            except Exception:
                return "Camera ke liye OpenCV install nahi hai, kripya OpenCV install karen."
        if face_cascade is None:
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except Exception:
                face_cascade = None
        # First check camera status
        status = camera.get_camera_status()
        if not status.get('initialized', False):
            return "Camera ko initialize karne ki koshish kar raha hun..."
        
        # Read frame — only allowed if GUI owns the camera
        ret, frame = camera.read_frame(owner='gui')
        if not ret or frame is None:
            # Fallback: try to use last saved image if available
            img_path = data_path('camera_view.jpg')
            if os.path.exists(img_path):
                try:
                    frame = cv2.imread(img_path)
                    if frame is None:
                        return "Camera respond nahi kar raha hai. Dobara koshish kar raha hun..."
                except Exception:
                    return "Camera respond nahi kar raha hai. Dobara koshish kar raha hun..."
            else:
                return "Camera respond nahi kar raha hai. Dobara koshish kar raha hun..."
        
        # Check frame quality
        if frame.size == 0:
            return "Camera se koi frame nahi mil raha hai."
        if np.mean(frame) < 5:
            return "Camera view bahut andhera hai. Lighting check karen."
        
        # Create description of what is seen
        description = []
        
        # Detect faces
        try:
            if face_cascade is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) > 0:
                    description.append(f"{len(faces)} log camera ke samne dikhai de rahe hain")
        except Exception:
            # If face detection fails, continue without faces
            pass
        
        # Basic image enhancements (subtle)
        frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=10)
        
        # Apply adaptive histogram equalization for better contrast
        try:
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge((l, a, b))
            frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        except Exception:
            # If CLAHE or color conversion fails, keep the enhanced frame as-is
            pass
        
        # Save the processed frame
        try:
            cv2.imwrite(data_path('camera_view.jpg'), frame)
        except Exception as e:
            print(f"Failed to save image: {e}")
        
        # Create description text
        if description:
            desc_text = ". ".join(description)
        else:
            light_level = np.mean(frame)
            if light_level > 200:
                desc_text = "Camera view bahut bright hai"
            elif light_level > 100:
                desc_text = "Camera view normal hai"
            else:
                desc_text = "Camera view thoda dark hai"
        
        # Save description
        try:
            with open(data_path('camera_view.txt'), 'w', encoding='utf-8') as f:
                f.write(desc_text)
        except Exception as e:
            print(f"Failed to save description: {e}")
        
        return desc_text
    
    except Exception as e:
        error_msg = f"Camera view lene me error aa gaya: {str(e)}"
        print(error_msg)
        return error_msg