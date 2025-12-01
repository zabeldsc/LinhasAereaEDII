from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
VOOS_FILE = BASE_DIR / "data" / "voos.json"
USER_KEYS_FILE = BASE_DIR / "data" / "user_keys.json"
RESERVAS_FILE = BASE_DIR / "data" / "reservas.json"
CLIENTES_FILE = BASE_DIR / "data" / "clientes.json"

def load_voos():
    if VOOS_FILE.exists():
        with VOOS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_voos(voos):
    VOOS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with VOOS_FILE.open("w", encoding="utf-8") as f:
        json.dump(voos, f, ensure_ascii=False, indent=4)

def load_user_keys():
    if USER_KEYS_FILE.exists():
        with USER_KEYS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_keys(user_keys):
    USER_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USER_KEYS_FILE.open("w", encoding="utf-8") as f:
        json.dump(user_keys, f, ensure_ascii=False, indent=4)
        
def load_reservas():
    if RESERVAS_FILE.exists():
        with RESERVAS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

def save_reservas(reservas):
    RESERVAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RESERVAS_FILE.open("w", encoding="utf-8") as f:
        json.dump(reservas, f, ensure_ascii=False, indent=4)
        
def load_clientes():
    if CLIENTES_FILE.exists():
        with CLIENTES_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

def save_clientes(clientes):
    CLIENTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CLIENTES_FILE.open("w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)