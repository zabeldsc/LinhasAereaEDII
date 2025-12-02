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
        flash('Voo não encontrado!', 'danger')
        return redirect(url_for('passageiro.consultar_voos'))
    
    if request.method == "POST":
        assentos = int(voo.get('num_assentos', 0))
        
        if assentos > 0:    
            
            reservas = current_app.config.get('RESERVAS', {})
            clientes = current_app.config.get('CLIENTES', []) 
            
            reserva_id = str(int(time.time()))
            cpf_form = request.form.get('cpf', '')
            usuario_email = session['usuario'] # Email da sessão
            
            cliente_atual = None
            
            for c in clientes:
                if c.get('email') == usuario_email:
                    cliente_atual = c
                    break
            
            if not cliente_atual:
                flash('Erro: Usuário não encontrado na base de dados.', 'danger')
                return redirect(url_for('user.logout')) # Força logout se der erro grave
            
            # Cria a reserva
            reservas[reserva_id] = {
                "voo_id": voo_id,
                "codigo": voo["codigo"],
                "origem": voo["origem"],
                "destino": voo["destino"],
                "milhas": voo["milhas"],
                "preco": voo["preco_passagem"],
                "aeronave": voo["tipo_aeronave"],
                "data_compra": time.strftime('%d-%m-%Y'),
                "cpf_passageiro": cpf_form,
                "usuario": usuario_email
            }
            
            # Atualiza o Cliente encontrado (Isso atualiza dentro da lista 'clientes' automaticamente)
            cliente_atual['cpf'] = cpf_form # Salva o CPF novo no cliente
            
            # Tratamento seguro para milhas
            milhas_str = cliente_atual.get('milhas')
            if not milhas_str: 
                milhas_str = 0
            cliente_atual['milhas'] = int(milhas_str) + int(voo['milhas'])
            
            # Tratamento da lista de reservas
            lista_reservas = cliente_atual.get('reservas', [])
            if isinstance(lista_reservas, str) or not isinstance(lista_reservas, list): 
                # Se vier como string "[]" do CSV, converte ou limpa
                lista_reservas = []
            
            lista_reservas.append(reserva_id)
            cliente_atual['reservas'] = lista_reservas
            
            # 3. Atualiza Voo
            voo['num_assentos'] = assentos - 1
            voos[voo_id] = voo
            
            # 4. Salva Tudo
            current_app.config['VOOS'] = voos
            current_app.config['RESERVAS'] = reservas
            current_app.config['CLIENTES'] = clientes 
            
            data.save_voos(voos)            
            data.save_reservas(reservas)
            data.save_clientes(clientes) # Salva a lista inteira novamente
            
            flash('Reserva feita com sucesso!', 'success') # Corrigido typo 'sucess'
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
