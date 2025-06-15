#!/usr/bin/env python3
import argparse
import cv2
import json
from db import Database
from face_encoder import FaceEncoder

def main():
    parser = argparse.ArgumentParser(description="Registrar un rostro en la BD")
    parser.add_argument("image", help="Ruta al archivo de imagen (rostro)")
    parser.add_argument("name", help="Nombre asociado al rostro")
    args = parser.parse_args()

    # Inicializar componentes
    db = Database()
    encoder = FaceEncoder()

    # 1) Cargar imagen
    img = cv2.imread(args.image)
    if img is None:
        print(f"[ERROR] No se pudo leer la imagen: {args.image}")
        return

    # 2) Generar embedding
    embedding = encoder.encode(img)

    # 3) Guardar en BD
    face_id = db.add_known_face(
        name=args.name,
        face_encoding=json.dumps(embedding.tolist()),
        photo_path=args.image
    )

    if face_id:
        print(f"[OK] Rostro '{args.name}' registrado con ID {face_id}.")
    else:
        print(f"[ERROR] No se pudo registrar el rostro (¿ya existe?).")

if __name__ == "__main__":
    main()
