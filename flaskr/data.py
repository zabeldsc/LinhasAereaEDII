import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VOOS_FILE = os.path.join(BASE_DIR, "voos.json")
USER_KEYS_FILE = os.path.join(BASE_DIR, "user_keys.json")

voos = {}
user_keys = {}

def load_voos():
    global voos
    if os.path.exists(VOOS_FILE):
        with open(VOOS_FILE, "r", encoding="utf-8") as f:
            voos = json.load(f)
    else:
        voos = {}

def save_voos():
    with open(VOOS_FILE, "w", encoding="utf-8") as f:
        json.dump(voos, f, ensure_ascii=False, indent=4)

def load_user_keys():
    global user_keys
    if os.path.exists(USER_KEYS_FILE):
        with open(USER_KEYS_FILE, "r", encoding="utf-8") as f:
            user_keys = json.load(f)
    else:
        user_keys = {}

def save_user_keys():
    with open(USER_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_keys, f, ensure_ascii=False, indent=4)
