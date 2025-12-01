from flask import Blueprint, redirect, render_template, current_app, request, session, url_for, flash
from app.blueprints.user_bp import login_required_passageiro
from app import data
import time

passageiro_bp = Blueprint('passageiro', __name__, url_prefix='/passageiro')

@passageiro_bp.route('/dashboard')
@login_required_passageiro
def dashboard():
    nome = session.get('nome')
    usuario = session.get('usuario')
    reservas = current_app.config.get('RESERVAS', {})
    reservas_user = {
        rid: r for rid, r in reservas.items()
        if r.get("usuario") == usuario
    }
    print("User atual:", session.get('usuario'))
    print("User reserva:", reservas_user)
    milhas = sum(int(reserva.get("milhas", 0)) for reserva in reservas_user.values())
    return render_template('passageiro/dashboard.html', nome=nome, milhas=milhas, reservas=reservas_user)

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

@passageiro_bp.route('/consultar_voos/reservar/<voo_id>', methods=['GET', 'POST'])
@login_required_passageiro
def reservar(voo_id):
    voos = current_app.config.get('VOOS', {})
    voo = voos.get(voo_id)
    
    if not voo:
        flash('Voo nao encontrado!', 'danger')
        return redirect(url_for('passageiro.consultar_voos'))
    
    if request.method == "POST":
        assentos = int(voo.get('num_assentos', 0))
        
        if assentos > 0:    
            
            reservas = current_app.config.get('RESERVAS', {})
            reserva = str(int(time.time()))
            
            #Passageiro confirma com cpf para ser a chave da gestao de clientes
            cpf_passageiro = request.form.get('cpf', '')
            usuario = session['usuario']
            reservas[reserva] = {
                "voo_id": voo_id,
                "codigo": voo["codigo"],
                "origem": voo["origem"],
                "destino": voo["destino"],
                "milhas": voo["milhas"],
                "preco": voo["preco_passagem"],
                "aeronave": voo["tipo_aeronave"],
                "data_compra": time.strftime('%d-%m-%Y'),
                "cpf_passageiro": cpf_passageiro,
                "usuario": usuario
            }
            current_app.config['RESERVAS'] = reservas
            data.save_reservas(reservas)
            
            #Decrescento assentos apos reserva e atualizo o dicionario de voos
            voo['num_assentos'] = assentos -1
            voos[voo_id] = voo
            current_app.config['VOOS'] = voos
            data.save_voos(voos)
            
            flash('Reserva feita com sucesso!', 'sucess')
            return redirect(url_for('passageiro.dashboard'))
        
        else:
            flash('Assentos esgotados!', 'danger')
            return redirect(url_for('passageiro.consultar_voos'))

    return render_template('passageiro/comprar.html', voo=voo, voo_id=voo_id)

@passageiro_bp.route('/simular_conexoes')
@login_required_passageiro
def simular_conexoes():
    voos = current_app.config.get('VOOS', {})
    # Aqui você poderia chamar sua função de grafo para simular conexões
    return render_template('passageiro/simular_conexoes.html', voos=voos)
