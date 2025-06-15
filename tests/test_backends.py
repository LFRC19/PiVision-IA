import cv2
import os

def list_video_devices():
    # Lista los nodos /dev/video*
    devices = sorted(os.listdir('/dev'))
    return [d for d in devices if d.startswith('video')]

def test_cameras(max_index=40):
    print("=== Dispositivos detectados (/dev/video*) ===")
    for dev in list_video_devices():
        print(f"/dev/{dev}")
    print("\n=== Prueba de apertura con OpenCV ===")
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        opened = cap.isOpened()
        cap.release()
        print(f"/dev/video{i:<2} | opened={opened}")

if __name__ == "__main__":
    test_cameras()
