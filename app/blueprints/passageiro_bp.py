from flask import Blueprint, redirect, render_template, current_app, session
from app.blueprints.user_bp import login_required_passageiro

passageiro_bp = Blueprint('passageiro', __name__, url_prefix='/passageiro')

@passageiro_bp.route('/dashboard')
@login_required_passageiro
def dashboard():
    usuario = session['usuario']
    voos = current_app.config.get('VOOS', {})
    reservas = current_app.config.get('RESERVAS', {}).get(usuario, [])
    milhas = sum(reserva.get("milhas", 0) for reserva in reservas)
    return render_template('passageiro/dashboard.html', usuario=usuario, milhas=milhas, reservas=reservas)

@passageiro_bp.route('/consultar_voos')
@login_required_passageiro
def consultar_voos():
    voos = current_app.config.get('VOOS', {})
    return render_template('passageiro/consultar_voos.html', voos=voos)

@passageiro_bp.route('/simular_conexoes')
@login_required_passageiro
def simular_conexoes():
    voos = current_app.config.get('VOOS', {})
    # Aqui você poderia chamar sua função de grafo para simular conexões
    return render_template('passageiro/simular_conexoes.html', voos=voos)
