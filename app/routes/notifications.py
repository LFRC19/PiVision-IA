import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash

notifications_bp = Blueprint("notifications", __name__)

CONFIG_PATH = os.path.join("config", "notifications.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            "email_enabled": False,
            "email_to": "",
            "cooldown_seconds": 60
        }
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


@notifications_bp.route("/dashboard/notifications", methods=["GET", "POST"])
def notifications():
    if request.method == "POST":
        email_enabled = "email_enabled" in request.form
        email_to = request.form.get("email_to", "").strip()
        cooldown = int(request.form.get("cooldown_seconds", 60))

        new_config = {
            "email_enabled": email_enabled,
            "email_to": email_to,
            "cooldown_seconds": cooldown
        }

        save_config(new_config)
        flash("✅ Configuración guardada exitosamente", "success")
        return redirect(url_for("notifications.notifications"))

    config = load_config()
    return render_template("notifications.html", config=config)
