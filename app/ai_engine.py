# app/ai_engine.py

import time
import cv2
import os
from datetime import datetime
from collections import deque
from dotenv import load_dotenv
import tflite_runtime.interpreter as tflite

from app.frame_processor      import FrameProcessor
from app.face_mesh_processor  import FaceMeshProcessor
from app.face_normalizer      import FaceNormalizer
from app.gesture_handler      import GestureHandler
from face_encoder             import FaceEncoder
from face_matcher             import FaceMatcher
from db                       import Database
from person_tracker           import CentroidTracker
from app.system_monitor       import get_system_metrics
from utils.notifier           import send_notification_if_gesture

# Cargar configuración desde .env
load_dotenv()

def load_tflite_model(model_path):
    use_tpu = os.getenv("USE_TPU", "false").lower() == "true"
    try:
        if use_tpu:
            from tflite_runtime.interpreter import load_delegate
            print("[INFO] Intentando usar IA Hat+ (Edge TPU)...")
            interpreter = tflite.Interpreter(
                model_path=model_path,
                experimental_delegates=[load_delegate('libedgetpu.so.1')]
            )
            print("[INFO] Inferencia acelerada activada con IA Hat+")
        else:
            print("[INFO] Modo CPU activado para inferencia")
            interpreter = tflite.Interpreter(model_path=model_path)
    except Exception as e:
        print(f"[WARNING] Error al cargar IA Hat+ ({e}), usando CPU por defecto")
        interpreter = tflite.Interpreter(model_path=model_path)

    interpreter.allocate_tensors()
    return interpreter

class AIPipeline:
    def __init__(self, cam_id, width, height):
        self.cam_id  = cam_id
        self.width   = width
        self.height  = height

        self.motion_proc     = FrameProcessor()
        self.mesh_processor  = FaceMeshProcessor()
        self.normalizer      = FaceNormalizer()
        self.encoder         = FaceEncoder()

        # Umbral dinámico desde .env
        threshold = float(os.getenv("FACE_MATCH_THRESHOLD", 0.6))
        self.matcher         = FaceMatcher(Database(), threshold=threshold)

        self.tracker         = CentroidTracker(max_disappeared=30, max_distance=50)
        self.gesture_handler = GestureHandler("sessions")

        self.track_hist = {}
        self.count_up   = set()
        self.count_down = set()
        self.recent_events = deque()

    def process(self, frame):
        events = []
        now = time.time()
        h, w = frame.shape[:2]

        # Movimiento
        _, contours = self.motion_proc.detect_motion(frame)
        if contours:
            events.append({"type": "motion", "n": len(contours)})

        # Rostros
        mesh_faces = self.mesh_processor.process(frame)
        face_count = 0
        rects = []

        for lm in mesh_faces:
            xs, ys = [int(p[0]) for p in lm], [int(p[1]) for p in lm]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            rect = (x0, y0, x1 - x0, y1 - y0)
            rects.append(rect)

            face = self.normalizer.normalize(frame, lm)
            if face is not None:
                emb_start = time.time()
                emb = self.encoder.encode(face)
                emb_time = time.time() - emb_start
                print(f"[DEBUG] Tiempo de inferencia facial: {emb_time:.3f} s")

                mres = self.matcher.match(emb)
                label = mres["name"] if mres else "Desconocido"
                events.append({"type": "face", "label": label})
                face_count += 1

        events.append({"type": "people_count", "count": face_count})

        # Gestos
        result = self.gesture_handler.analyze(self.cam_id, frame)

        if isinstance(result, tuple):
            g_evt, image_path = result
        else:
            g_evt, image_path = result, None

        if g_evt:
            events.append({"type": "gesture", "gesture": g_evt})
            if image_path:
                send_notification_if_gesture(image_path)

        # Tracking
        LINE = h // 2
        cv2.line(frame, (0, LINE), (w, LINE), (255, 0, 0), 2)

        objs = self.tracker.update(rects)
        for oid, (cx, cy) in objs.items():
            prev = self.track_hist.get(oid, cy)
            self.track_hist[oid] = cy
            if prev < LINE <= cy and oid not in self.count_down:
                self.count_down.add(oid)
                events.append({"type": "cross", "dir": "down", "id": oid})
            elif prev > LINE >= cy and oid not in self.count_up:
                self.count_up.add(oid)
                events.append({"type": "cross", "dir": "up", "id": oid})

            cv2.putText(frame, str(oid), (cx, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            cv2.rectangle(frame, (cx-5, cy-5), (cx+5, cy+5), (0,255,0), 1)

        for (x, y, w0, h0) in rects:
            cv2.rectangle(frame, (x, y), (x+w0, y+h0), (0,255,255), 1)

        # Timestamps
        ts = datetime.now().isoformat()
        for evt in events:
            evt["timestamp"] = ts
            self.recent_events.append(evt)

        return frame, events

    def get_last_events(self):
        events = list(self.recent_events)
        self.recent_events.clear()
        events.append(get_system_metrics())
        return events
