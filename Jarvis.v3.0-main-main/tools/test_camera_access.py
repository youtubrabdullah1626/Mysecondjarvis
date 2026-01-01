"""Quick camera access tester for Jarvis workspace.
Run with: venv\Scripts\python.exe tools/test_camera_access.py
"""
import sys, os, time
# Ensure project root is on sys.path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

print(f"Project root: {root}")

try:
    from features.camera_manager import camera
except Exception as e:
    print("Failed to import camera manager:", e)
    raise

print("Calling camera.start(owner='test')...")
ok, msg = camera.start(owner='test')
print("camera.start ->", ok, msg)

status = camera.get_camera_status()
print("get_camera_status ->", status)

print("Trying read_frame()...")
ret, frame = camera.read_frame()
print("read_frame ->", ret, 'frame' if frame is not None else None)

if ret and frame is not None:
    # save a debug image
    try:
        from features.storage import data_path
        outp = data_path('camera_test_output.jpg')
        import cv2
        cv2.imwrite(outp, frame)
        print(f"Saved frame to {outp}")
    except Exception as e:
        print("Failed to save frame:", e)

print("Stopping camera (owner='test')...")
ok2, msg2 = camera.stop(owner='test')
print("camera.stop ->", ok2, msg2)

print("Done")
