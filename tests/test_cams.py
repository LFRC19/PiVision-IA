import cv2

for idx in (0, 2):
    cap = cv2.VideoCapture(idx)
    print(f"Índice {idx}: {'OK' if cap.isOpened() else 'NO'}")
    if cap.isOpened():
        ret, frame = cap.read()
        print(f"  Frame leído: {'Sí' if ret else 'No'}")
    cap.release()
