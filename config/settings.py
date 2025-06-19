# config/settings.py
SECRET_KEY = '…'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/pivision.db'
DEBUG = True

# IDs de tus cámaras (pueden ser índices 0, 1, 2… o cadenas con device paths)
CAMERA_IDS = [0]

EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_FROM = "pivision.alerts@gmail.com"
EMAIL_PASSWORD = "gkja ntyb gono aynv"
EMAIL_TO = "luisfernandorc16@gmail.com"
