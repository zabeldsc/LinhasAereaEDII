from flask import Flask, redirect
from .blueprints.admin_bp import admin_bp
from .blueprints.passageiro_bp import passageiro_bp
from . import data
from datetime import datetime
import os

def create_app():
    app = Flask(__name__)

    # Chave secreta necessária para sessões
    app.secret_key = os.urandom(24)

    # Registrar blueprints
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(passageiro_bp, url_prefix="/passageiro")

    # Context processor
    @app.context_processor
    def inject_year():
        return {"year": datetime.now().year}

    # Carregar dados
    app.config['VOOS'] = data.load_voos()
    app.config['USER_KEYS'] = data.load_user_keys()

    # Rota raiz
    @app.route('/')
    def raiz():
        return redirect("/passageiro/")

    return app
