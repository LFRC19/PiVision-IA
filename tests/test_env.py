from dotenv import load_dotenv
import os

load_dotenv()  # carga las variables desde .env

print("USE_TPU =", os.getenv("USE_TPU"))
print("FACE_MATCH_THRESHOLD =", os.getenv("FACE_MATCH_THRESHOLD"))

