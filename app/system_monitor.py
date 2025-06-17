# app/system_monitor.py

import psutil
import shutil
import datetime

def get_system_metrics():
    """
    Retorna las métricas básicas del sistema en forma de diccionario.
    Incluye uso de CPU, memoria RAM, y disco principal.
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = shutil.disk_usage("/")

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "metrics",
            "cpu": round(cpu_percent, 1),              # en %
            "memory": round(memory.percent, 1),        # en %
            "disk": round(disk.used / disk.total * 100, 1)  # en %
        }
    except Exception as e:
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "metrics",
            "error": str(e)
        }
