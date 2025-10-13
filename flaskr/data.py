from flask import Flask
import os
import json

voos = {}
user_keys = {}

VOOS_FILE = "voos.json"
USER_KEYS_FILE = "user_keys.json"

def load_voos():
    global voos

    if os.path.exists(VOOS_FILE):
        with open(VOOS_FILE, 'r') as f:
            voos = json.load(f)

def save_voos():
    with open(VOOS_FILE, 'w') as f:
         json.dump(voos, f, indent=4)


def load_user_keys():
    global user_keys

    if os.path.exists(USER_KEYS_FILE):
        with open(USER_KEYS_FILE, 'r') as f:
            user_keys = json.load(f)

def save_user_keys():
    with open(USER_KEYS_FILE, 'w') as f:
        json.dump(user_keys, f, indent=4)