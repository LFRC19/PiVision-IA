import numpy as np

KEYPOINTS = [33, 263, 1, 13, 14]  # ojos, nariz, boca

def extract_signature(landmarks, frame_shape):
    """
    Recibe una lista de landmarks [(x, y), ...] y devuelve un array normalizado [x1, y1, x2, y2, ...]
    """
    h, w = frame_shape[:2]
    signature = []
    for idx in KEYPOINTS:
        x, y = landmarks[idx]
        signature.extend([x / w, y / h])
    return np.array(signature)

def is_similar(sig1, sig2, threshold=0.05):
    """
    Compara dos firmas faciales normalizadas.
    Retorna True si son similares (distancia euclidiana < threshold)
    """
    if sig1 is None or sig2 is None:
        return False
    dist = np.linalg.norm(sig1 - sig2)
    return dist < threshold
