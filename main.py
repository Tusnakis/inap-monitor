import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup

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

def send_telegram_message(text):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    response = requests.post(url, json=payload)
    response.raise_for_status()

def get_relevant_hash(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

     # 1. Encontrar TODOS los h3 cuyo texto sea EXACTAMENTE "Ejercicio único"
    h3s = [h for h in soup.find_all("h3") if h.get_text(strip=True) == "Ejercicio único"]

    if len(h3s) < 2:
        raise Exception("No existe un segundo h3 con el texto 'Ejercicio único'")

    segundo_h3 = h3s[1]

    # 2. Encontrar la lista inmediatamente después del segundo h3
    #    (puede ser ul, ol, div con items, etc.)
    lista = segundo_h3.find_next(["ul", "ol"])

    if lista is None:
        raise Exception("El segundo h3 no tiene una lista después")

    # 3. Extraer el texto de todos los nodos de la lista
    content = lista.get_text(separator=" ", strip=True)

    # 4. Calcular hash
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def run():
    print("Comprobando cambios en INAP...")

    url = "https://sede.inap.gob.es/es/procedimientos-y-servicios/seleccion/procesos-selectivos-de-cuerpos-y-escalas-generales/cuerpo-de-tecnicos-auxiliares-de-informatica-de-la-administracion-del-estado-ingreso-libre-convocatoria-2025"
    new_hash = get_relevant_hash(url)

    state = load_state()
    old_hash = state.get("hash", "")

    if new_hash != old_hash:
        print("Nuevo contenido detectado")
        send_telegram_message("🔔 Nuevo contenido detectado en INAP (TAI 2025)")
        save_state({"hash": new_hash})
    else:
        print("Sin cambios")

if __name__ == "__main__":
    run()
