import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
import datetime

URL = "https://sede.inap.gob.es/es/procedimientos-y-servicios/seleccion/procesos-selectivos-de-cuerpos-y-escalas-generales/cuerpo-de-tecnicos-auxiliares-de-informatica-de-la-administracion-del-estado-ingreso-libre-convocatoria-2025"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STATE_FILE = "state.json"


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=payload)


def get_page_content():
    response = requests.get(URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extraemos solo el contenido principal
    main_content = soup.get_text(separator="\n", strip=True)
    return main_content


def compute_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_state():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(hash_value):
    with open(STATE_FILE, "w") as f:
        json.dump({"hash": hash_value}, f)


def run():
    print("Comprobando cambios en INAP...")
    content = get_page_content()
    new_hash = compute_hash(content)

    state = load_state()

    if state is None:
        print("No hay estado previo, guardando estado inicial.")
        save_state(new_hash)
        return

    if new_hash != state["hash"]:
        print("¡Nuevo contenido detectado!")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = (
            f"⚠️ Nuevo contenido detectado en INAP ({timestamp})\n\n"
            f"URL: {URL}\n\n"
            f"Contenido nuevo:\n\n{content[:3500]}"
        )

        send_telegram_message(message)
        save_state(new_hash)
    else:
        print("Sin cambios.")


if __name__ == "__main__":
    run()
