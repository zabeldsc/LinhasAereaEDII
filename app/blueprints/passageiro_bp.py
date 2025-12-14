from flask import Blueprint, redirect, render_template, current_app, request, session, url_for, flash
from app.blueprints.user_bp import login_required_passageiro
from app import data
from app.search_structures.grafo import Grafo
import time, random, folium
from datetime import datetime, timedelta

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
        
        #Pega o valor escolhido pelo user no site
        data_viagem_input = request.form.get('data_viagem')
        if data_viagem_input:
            try:
                objeto_data = datetime.strptime(data_viagem_input, '%Y-%m-%d')
                data_viagem_str = objeto_data.strftime('%d-%m-%Y')
            except ValueError:
                data_viagem_str = time.strftime('%d-%m-%Y')
        #Se nao houver data inserida, eu gero a viagem sendo entre 7-15 dias apos reserva
        else:
            hoje = datetime.now()
            valor_aleatorio = random.randint(7, 15)
            data_futura = hoje + timedelta(days=valor_aleatorio)
            data_viagem_str = data_futura.strftime('%d-%m-%Y')

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
            "data_viagem": data_viagem_str,
            "cpf_passageiro": cpf_passageiro,
            "usuario": usuario_email
        }

        # Atualizar milhas
        cliente["milhas"] = int(cliente.get("milhas", 0)) + int(voo["milhas"])
        
        cliente["data_viagem"] = data_viagem_str

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

        flash(f"Reserva confirmada! Sua viagem será em {data_viagem_str}.", "success")
        return redirect(url_for("passageiro.dashboard"))

    return render_template("passageiro/comprar.html", voo=voo, voo_id=voo_id)

@passageiro_bp.route('/simular_conexoes')
@login_required_passageiro
def simular_conexoes():
    origem = request.args.get("origem")
    destino = request.args.get("destino")
    coordenadas = data.load_coordenadas()
    grafo = current_app.config["GRAFO"]
    listar_aeroportos = sorted(coordenadas.keys())
    mapa_html = None
    rota = None

    if origem and destino:
        rota = grafo.dijkstra(origem, destino)
        
        if rota:
            
            #Crio o mapa base
            mapa_base = folium.Map(location=[-15.793889, -47.882778], zoom_start=4)
            
            #lista para guardar as conexoes lat,long
            pontos_trajeto = []
            
            #Pega o primeiro ponto(origem)
            primeiro_voo = rota["trechos"][0]
            pontos_trajeto.append(primeiro_voo["origem"])
            
            for trecho in rota["trechos"]:
                pontos_trajeto.append(trecho["destino"])

            #pega as coordenadas baseado nas chaves previamente coletadas
            lista_coordenadas = []
            for ponto in pontos_trajeto:
                if ponto in coordenadas:
                    lat, lon = coordenadas[ponto]
                    lista_coordenadas.append([lat, lon])
                    
                    #Adiciono os marcadores das coordenadas
                    folium.Marker(
                        location=[lat, lon],
                        tooltip=ponto,
                        icon=folium.Icon(color="blue", icon="plane")
                    ).add_to(mapa_base)
            
            folium.PolyLine(
                locations=lista_coordenadas,
                color="red",
                weight=2.5,
                opacity=1
            ).add_to(mapa_base)
            
            mapa_html = mapa_base._repr_html_()

    return render_template(
        "passageiro/simular_conexoes.html",
        origem=origem,
        destino=destino,
        rota=rota,
        mapa=mapa_html,
        aeroportos=listar_aeroportos
    )
