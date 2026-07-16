import os
import json
import hashlib
import requests

STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"hash": ""}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"hash": ""}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_page_hash(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content = response.text.encode("utf-8")
    return hashlib.sha256(content).hexdigest()

def run():
    print("Comprobando cambios en INAP...")

    url = "https://sede.inap.gob.es/es/procedimientos-y-servicios/seleccion/procesos-selectivos-de-cuerpos-y-escalas-generales/cuerpo-de-tecnicos-auxiliares-de-informatica-de-la-administracion-del-estado-ingreso-libre-convocatoria-2025"
    new_hash = get_page_hash(url)

    state = load_state()
    old_hash = state.get("hash", "")

    if new_hash != old_hash:
        print("Nuevo contenido detectado")
        # Aquí envías el mensaje a Telegram
        save_state({"hash": new_hash})
    else:
        print("Sin cambios")

if __name__ == "__main__":
    run()
