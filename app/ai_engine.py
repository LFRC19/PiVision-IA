# app/ai_engine.py
import time, cv2, json
from datetime import datetime
from app.frame_processor      import FrameProcessor
from app.face_mesh_processor  import FaceMeshProcessor
from app.face_normalizer      import FaceNormalizer
from app.gesture_handler      import GestureHandler
from face_encoder  import FaceEncoder
from face_matcher  import FaceMatcher
from db            import Database
from person_tracker import CentroidTracker

class AIPipeline:
    def __init__(self, cam_id, width, height):
        self.cam_id  = cam_id
        self.width   = width
        self.height  = height

        # --- inicializas tus componentes tal cual vision.py ---
        self.motion_proc    = FrameProcessor()
        self.mesh_processor = FaceMeshProcessor()
        self.normalizer     = FaceNormalizer()
        self.encoder        = FaceEncoder()
        self.matcher        = FaceMatcher(Database(), threshold=0.6)
        self.tracker        = CentroidTracker(max_disappeared=30, max_distance=50)
        self.gesture_handler = GestureHandler("sessions")

        # Historial para conteo
        self.track_hist = {}
        self.count_up   = set()
        self.count_down = set()
        self.last_face  = 0.0
        self.cooldown   = 5.0

        # Almacenamiento de eventos recientes
        self.last_events = []

    def process(self, frame):
        """
        Devuelve:
          - frame_annot: frame con overlays
          - events: lista de dicts con eventos (json-serializable)
        """
        events = []
        now = time.time()
        h, w = frame.shape[:2]

        # 1- Detección de movimiento
        thresh, contours = self.motion_proc.detect_motion(frame)
        if contours:
            events.append({"type": "motion", "n": len(contours)})

        # 2- Rostros
        rects = []
        mesh_faces = self.mesh_processor.process(frame)
        for lm in mesh_faces:
            xs, ys = [int(p[0]) for p in lm], [int(p[1]) for p in lm]
            x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            rects.append((x0, y0, x1 - x0, y1 - y0))

            if now - self.last_face >= self.cooldown:
                face = self.normalizer.normalize(frame, lm)
                if face is not None:
                    emb  = self.encoder.encode(face)
                    mres = self.matcher.match(emb)
                    label = mres["name"] if mres else "Desconocido"
                    events.append({"type": "face", "label": label})
                    self.last_face = now

        # 3- Gestos
        g_evt = self.gesture_handler.analyze(self.cam_id, frame)
        if g_evt:
            events.append({"type": "gesture", "gesture": g_evt})

        # 4- Tracking y conteo
        objs = self.tracker.update(rects)
        LINE = h // 2
        cv2.line(frame, (0, LINE), (w, LINE), (255, 0, 0), 2)

        for oid, (cx, cy) in objs.items():
            prev = self.track_hist.get(oid, cy)
            self.track_hist[oid] = cy
            if prev < LINE <= cy and oid not in self.count_down:
                self.count_down.add(oid)
                events.append({"type": "cross", "dir": "down"})
            elif prev > LINE >= cy and oid not in self.count_up:
                self.count_up.add(oid)
                events.append({"type": "cross", "dir": "up"})

            cv2.putText(frame, f"{oid}", (cx, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            cv2.rectangle(frame, (cx-5, cy-5), (cx+5, cy+5), (0,255,0), 1)

        for (x, y, w0, h0) in rects:
            cv2.rectangle(frame, (x, y), (x+w0, y+h0), (0,255,255), 1)

        # Guardar eventos recientes
        self.last_events = events

        return frame, events

    def get_last_events(self):
        return self.last_events
