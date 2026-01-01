"""Face registry helper (lightweight stub)

Functions:
- register_face(name: str, image_path: str) -> bool
- identify_face(image_path: str) -> str | None

This is a minimal implementation that tries to use the `face_recognition` library if present.
If not available, functions return safe fallbacks.
"""
import os

def register_face(name: str, image_path: str) -> bool:
    """Register a face image under the given name (copy into a local registry).
    Returns True on success, False otherwise."""
    try:
        registry_dir = os.path.join(os.path.dirname(__file__), 'face_db')
        os.makedirs(registry_dir, exist_ok=True)
        if not os.path.exists(image_path):
            return False
        dest = os.path.join(registry_dir, f"{name}.jpg")
        with open(image_path, 'rb') as src, open(dest, 'wb') as dst:
            dst.write(src.read())
        return True
    except Exception as e:
        print(f"[face_registry] register_face error: {e}")
        return False

def identify_face(image_path: str):
    """Try to identify a face in image_path against registered faces. Returns name or None.
    This is a stub: if `face_recognition` is available it will attempt to match, otherwise returns None."""
    try:
        import importlib
        face_recognition = importlib.import_module('face_recognition')
    except Exception:
        print("[face_registry] face_recognition not installed; identify_face not available.")
        return None

    try:
        registry_dir = os.path.join(os.path.dirname(__file__), 'face_db')
        known_encodings = []
        known_names = []
        if not os.path.exists(registry_dir):
            return None
        for f in os.listdir(registry_dir):
            path = os.path.join(registry_dir, f)
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if enc:
                known_encodings.append(enc[0])
                known_names.append(os.path.splitext(f)[0])
        unknown_img = face_recognition.load_image_file(image_path)
        unknown_encs = face_recognition.face_encodings(unknown_img)
        if not unknown_encs:
            return None
        results = face_recognition.compare_faces(known_encodings, unknown_encs[0])
        for match, name in zip(results, known_names):
            if match:
                return name
        return None
    except Exception as e:
        print(f"[face_registry] identify_face error: {e}")
        return None
