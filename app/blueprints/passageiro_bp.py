from flask import Blueprint, redirect, render_template, current_app, request, session, url_for, flash
from app.blueprints.user_bp import login_required_passageiro
from app import data
from app.search_structures.grafo import Grafo
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
    # Sempre recarrega voos atualizados
    voos = data.load_voos()
    voo = voos.get(voo_id)

    if not voo:
        flash("Voo não encontrado!", "danger")
        return redirect(url_for("passageiro.consultar_voos"))

    if request.method == "POST":
        assentos = int(voo.get("num_assentos", 0))
        if assentos <= 0:
            flash("Assentos esgotados!", "danger")
            return redirect(url_for("passageiro.consultar_voos"))

        # Carregar sempre a base atualizada
        clientes = data.load_clientes()
        reservas = data.load_reservas()

        usuario_email = session['usuario']

        # Encontrar cliente atual
        cliente = next((c for c in clientes if c["email"] == usuario_email), None)
        if not cliente:
            flash("Erro: cliente não encontrado.", "danger")
            return redirect(url_for("passageiro.dashboard"))

        cpf_passageiro = cliente.get("cpf")

        # Criar ID único da reserva
        reserva_id = str(int(time.time()))

        # Nova reserva
        reservas[reserva_id] = {
            "voo_id": voo_id,
            "codigo": voo["codigo"],
            "origem": voo["origem"],
            "destino": voo["destino"],
            "milhas": voo["milhas"],
            "preco": voo["preco_passagem"],
            "aeronave": voo["tipo_aeronave"],
            "data_compra": time.strftime('%d-%m-%Y'),
            "cpf_passageiro": cpf_passageiro,
            "usuario": usuario_email
        }

        # Atualizar milhas
        cliente["milhas"] = int(cliente.get("milhas", 0)) + int(voo["milhas"])

        # Garantir lista de reservas válida
        if not isinstance(cliente.get("reservas"), list):
            cliente["reservas"] = []
        cliente["reservas"].append(reserva_id)

        # Decrementar assentos
        voo["num_assentos"] = assentos - 1

        # Salvamentos
        data.save_voos(voos)
        data.save_reservas(reservas)
        data.save_clientes(clientes)

        # Sincronizar opcionalmente o config (não obrigatório mais)
        current_app.config["VOOS"] = voos
        current_app.config["RESERVAS"] = reservas
        current_app.config["CLIENTES"] = clientes

        flash("Reserva realizada com sucesso!", "success")
        return redirect(url_for("passageiro.dashboard"))

    return render_template("passageiro/comprar.html", voo=voo, voo_id=voo_id)

@passageiro_bp.route('/simular_conexoes')
@login_required_passageiro
def simular_conexoes():
    origem = request.args.get("origem")
    destino = request.args.get("destino")

    grafo = current_app.config["GRAFO"]
    rota = None

    if origem and destino:
        rota = grafo.dijkstra(origem, destino)

    return render_template(
        "passageiro/simular_conexoes.html",
        origem=origem,
        destino=destino,
        rota=rota
    )
