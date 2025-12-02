from pathlib import Path
import json
import csv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

VOOS_FILE = DATA_DIR / "voos.json"
ADM_KEYS_FILE = DATA_DIR / "adm_keys.json"
CLIENTES_FILE = DATA_DIR / "clientes.csv"
RESERVAS_FILE = DATA_DIR / "reservas.json"

# ----------------------------
# JSON HELPERS
# ----------------------------

def load_json(path):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ----------------------------
# JSON FILES
# ----------------------------

def load_voos():
    return load_json(VOOS_FILE)

def save_voos(voos):
    save_json(VOOS_FILE, voos)

def load_adm_keys():
    return load_json(ADM_KEYS_FILE)

def save_adm_keys(adm_keys):
    save_json(ADM_KEYS_FILE, adm_keys)

# ----------------------------
# CSV HELPERS (Clientes)
# ----------------------------

def load_clientes():
    if not CLIENTES_FILE.exists():
        return []

    clientes = []
    with CLIENTES_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clientes.append(row)
    return clientes

FIELDNAMES_CLIENTES = ["cpf", "nome", "email", "senha", "codigo_reserva", "data_viagem", "milhas", "reservas"]

def save_clientes(clientes):
    CLIENTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with CLIENTES_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES_CLIENTES)
        writer.writeheader()
        writer.writerows(clientes)
