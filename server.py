# server.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Desactivamos el reloader para que solo haya un único proceso
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )




