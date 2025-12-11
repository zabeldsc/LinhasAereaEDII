from pathlib import Path
import json, csv, ast
from app.search_structures.arvoreB import ArvoreB

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
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
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
    
def load_reservas():
    return load_json(RESERVAS_FILE)

def save_reservas(reservas):
    save_json(RESERVAS_FILE, reservas)

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

# ----------------------------
# BTree HELPERS
# ----------------------------

def load_tree_cpf():
    clientes = load_clientes()
    
    arvore = ArvoreB(3)
    for cliente in clientes:
        reservas = cliente.get('reservas')
        
        # Se for string (ex: "['123', '456']"), converte para lista real
        if isinstance(reservas, str):
            try:
                # ast.literal_eval converte a string com formato de lista para lista Python
                # Se a string for vazia ou "[]", vira uma lista vazia []
                if not reservas or reservas == "":
                    cliente['reservas'] = []
                else:
                    cliente['reservas'] = ast.literal_eval(reservas)
            except (ValueError, SyntaxError):
                # Se der erro na conversão, assume lista vazia para não quebrar o site
                cliente['reservas'] = []
        
        # Se for None, vira lista vazia
        elif reservas is None:
            cliente['reservas'] = []
        
        cpf_extraido = cliente.get('cpf')
        cpf = cpf_extraido.strip()
        if cpf:
            arvore.inserir(cpf, cliente)
    
    return arvore
            
def load_tree_nomes():
    clientes = load_clientes()
    arvore_nomes = ArvoreB(3)
    for cliente in clientes:
        reservas = cliente.get('reservas')        
        # Se for string (ex: "['123', '456']"), converte para lista real
        if isinstance(reservas, str):
            try:
                # ast.literal_eval converte a string com formato de lista para lista Python
                # Se a string for vazia ou "[]", vira uma lista vazia []
                if not reservas or reservas == "":
                    cliente['reservas'] = []
                else:
                    cliente['reservas'] = ast.literal_eval(reservas)
            except (ValueError, SyntaxError):
                # Se der erro na conversão, assume lista vazia para não quebrar o site
                cliente['reservas'] = []
        
        # Se for None, vira lista vazia
        elif reservas is None:
            cliente['reservas'] = []

        nome_completo = cliente.get('nome', '').strip().upper()
        if nome_completo:
            lista = arvore_nomes.buscar(nome_completo)
            if lista:
                lista.append(cliente)
            else:
                arvore_nomes.inserir(nome_completo, [cliente])
    
    return arvore_nomes