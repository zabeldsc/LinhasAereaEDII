from flask import Blueprint, redirect, render_template, current_app, request, session
from app.blueprints.user_bp import login_required_passageiro

passageiro_bp = Blueprint('passageiro', __name__, url_prefix='/passageiro')

@passageiro_bp.route('/dashboard')
@login_required_passageiro
def dashboard():
    nome = session['nome']
    voos = current_app.config.get('VOOS', {})
    reservas = current_app.config.get('RESERVAS', {}).get(nome, [])
    milhas = sum(reserva.get("milhas", 0) for reserva in reservas)
    return render_template('passageiro/dashboard.html', nome=nome, milhas=milhas, reservas=reservas)

@passageiro_bp.route('/consultar_voos', methods=['GET', 'POST'])
@login_required_passageiro
def consultar_voos():
    voos = current_app.config.get('VOOS', {})
    filtro_origem = request.args.get('origem', '')
    filtro_destino = request.args.get('destino', '')

    voos_filtrados = {
        k: v for k, v in voos.items()
        if (filtro_origem.lower() in v['origem'].lower()) and
           (filtro_destino.lower() in v['destino'].lower())
    }

    return render_template('passageiro/consultar_voos.html', voos=voos_filtrados,
                           filtro_origem=filtro_origem, filtro_destino=filtro_destino)


@passageiro_bp.route('/simular_conexoes')
@login_required_passageiro
def simular_conexoes():
    voos = current_app.config.get('VOOS', {})
    # Aqui você poderia chamar sua função de grafo para simular conexões
    return render_template('passageiro/simular_conexoes.html', voos=voos)
