import cv2
import time

def test_camera():
    print("Testing camera access...")
    
    # Try different camera indices
    for idx in range(2):
        print(f"\nTrying camera index {idx}")
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # Try DirectShow first
        
        if not cap.isOpened():
            print(f"Could not open camera {idx}")
            continue
            
        print(f"Successfully opened camera {idx}")
        
        # Try to read a frame
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame")
            cap.release()
            continue
            
        print(f"Successfully read frame: {frame.shape}")
        
        # Save the frame
        cv2.imwrite(f'camera_test_{idx}.jpg', frame)
        print(f"Saved frame to camera_test_{idx}.jpg")
        
        cap.release()
        
    print("\nTest complete")

if __name__ == "__main__":
    test_camera()