# app/ai_engine.py

import time
import cv2
from datetime import datetime
from collections import deque
from app.frame_processor      import FrameProcessor
from app.face_mesh_processor  import FaceMeshProcessor
from app.face_normalizer      import FaceNormalizer
from app.gesture_handler      import GestureHandler
from face_encoder             import FaceEncoder
from face_matcher             import FaceMatcher
from db                       import Database
from person_tracker           import CentroidTracker
from app.system_monitor       import get_system_metrics

class AIPipeline:
    def __init__(self, cam_id, width, height):
        self.cam_id  = cam_id
        self.width   = width
        self.height  = height

        # Componentes de visión
        self.motion_proc     = FrameProcessor()
        self.mesh_processor  = FaceMeshProcessor()
        self.normalizer      = FaceNormalizer()
        self.encoder         = FaceEncoder()
        self.matcher         = FaceMatcher(Database(), threshold=0.6)
        self.tracker         = CentroidTracker(max_disappeared=30, max_distance=50)
        self.gesture_handler = GestureHandler("sessions")

        # Tracking y conteo
        self.track_hist = {}
        self.count_up   = set()
        self.count_down = set()

        # Cola para acumular eventos hasta que el frontend los consuma
        self.recent_events = deque()

    def process(self, frame):
        """
        Procesa un frame:
         - Detecta movimiento, rostros, gestos y cruces de línea  
         - Registra cada evento inmediatamente en self.recent_events  
        Retorna el frame con overlays y la lista de eventos del frame.
        """
        events = []
        now = time.time()
        h, w = frame.shape[:2]

        # 1) Movimiento
        _, contours = self.motion_proc.detect_motion(frame)
        if contours:
            events.append({"type": "motion", "n": len(contours)})

        # 2) Detección de rostros y normalización
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
                emb = self.encoder.encode(face)
                mres = self.matcher.match(emb)
                label = mres["name"] if mres else "Desconocido"
                events.append({"type": "face", "label": label})
                face_count += 1

        # Emitimos evento de conteo de personas detectadas en la cámara
        events.append({"type": "people_count", "count": face_count})

        # 3) Gestos
        g_evt = self.gesture_handler.analyze(self.cam_id, frame)
        if g_evt:
            events.append({"type": "gesture", "gesture": g_evt})

        # 4) Tracking y cruces de línea
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

        # overlays de rostros
        for (x, y, w0, h0) in rects:
            cv2.rectangle(frame, (x, y), (x+w0, y+h0), (0,255,255), 1)

        # Registrar todos los eventos con timestamp
        ts = datetime.now().isoformat()
        for evt in events:
            evt["timestamp"] = ts
            self.recent_events.append(evt)

        return frame, events

    def get_last_events(self):
        """
        Devuelve todos los eventos acumulados desde la última llamada,
        más un evento 'metrics' con CPU/RAM/Disco.
        Luego vacía la cola para no repetirlos.
        """
        events = list(self.recent_events)
        self.recent_events.clear()
        events.append(get_system_metrics())
        return events