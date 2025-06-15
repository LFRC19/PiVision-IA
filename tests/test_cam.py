# test_cam_server.py
from flask import Flask, Response
import cv2

app = Flask(__name__)

@app.route('/test_cam')
def test_cam():
    # Intentamos abrir sólo la cámara 0
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "ERROR: no se pudo abrir la cámara 0", 500

    # Leemos un solo frame
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return "ERROR: no se pudo leer un frame", 500

    # Codificamos a JPEG
    ret, jpeg = cv2.imencode('.jpg', frame)
    if not ret:
        return "ERROR: no se pudo codificar JPEG", 500

    # Devolvemos la imagen con el tipo de contenido adecuado
    return Response(jpeg.tobytes(), mimetype='image/jpeg')

if __name__ == '__main__':
    # Desactivamos el reloader por simplicidad
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
