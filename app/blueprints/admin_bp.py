from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import time, string, ast
from app import data
from app.blueprints.user_bp import login_required_admin
from app.search_structures.arvoreB import ArvoreB
from app.search_structures.lat_lon_search import buscar_coordenada

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/voos')
@login_required_admin
def pagina_voos():
    voos = current_app.config.get('VOOS', {})
    return render_template('admin/voos.html', voos=voos)

@admin_bp.route('/clientes', methods=['GET', 'POST'])
@login_required_admin
def pagina_clientes():
    lista_clientes = current_app.config.get('CLIENTES', [])
            
    cpf_busca = request.args.get('buscar_cpf') or request.form.get('buscar_cpf')
    nome_busca = request.args.get('buscar_nome') or request.args.get('buscar_nome')
    letra_inicial = request.args.get('letra')
    
    clientes_para_exibir = []
    
    if cpf_busca:
        arvore = current_app.config.get('ARVORE_CLIENTES_CPF')
        
        if arvore:
            resultado = arvore.buscar(cpf_busca.strip())
            
            if resultado:
                clientes_para_exibir = [resultado] # Coloca em lista para o template iterar
                flash(f'Cliente encontrado: {resultado.get("nome")}', 'success')
            else:
                clientes_para_exibir = [] # Lista vazia se não achar
                flash('CPF não encontrado.', 'warning')
                
        else:
            flash('Erro: Estrutura de busca por CPF não carregada.', 'danger')
            
    elif nome_busca:
        arvore_nomes = current_app.config.get('ARVORE_CLIENTES_NOME')
        
        if arvore_nomes:
            termo_upper = nome_busca.upper()
            resultado_nomes = arvore_nomes.buscar_parcial(termo_upper)
        
            if resultado_nomes:
                clientes_para_exibir = resultado_nomes
                flash(f'{len(resultado_nomes)} cliente(s) encontrado(s) com este nome.', 'success')              
            else:
                clientes_para_exibir = [] # Lista vazia se não achar
                flash('Nome exato não encontrado na Árvore.', 'warning')
        else:
            flash('Erro ao carregar árvore de nomes.', 'danger')
    
    elif letra_inicial:
        clientes_para_exibir = [
            c for c in lista_clientes 
            if c.get('nome', '').strip().upper().startswith(letra_inicial.upper())
        ]
        if not clientes_para_exibir:
            flash(f'Nenhum cliente começa com a letra {letra_inicial}.', 'info')

    else:
        clientes_para_exibir = lista_clientes
        
    # Gerar lista ['A', 'B', 'C'...] para o HTML
    alfabeto = list(string.ascii_uppercase)

    return render_template('admin/clientes.html', clientes=clientes_para_exibir, alfabeto=alfabeto)

@admin_bp.route('/voos/add', methods=['GET', 'POST'])
@login_required_admin
def add_voos():
    if request.method == "POST":
        voos = current_app.config.get('VOOS', {})
        coordenadas = current_app.config.get('COORDENADAS', {})
        
        voo_id = str(int(time.time()))
        voos[voo_id] = {
            "codigo": request.form["codigo"],
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": request.form["milhas"],
            "preco_passagem": request.form["preco_passagem"],
            "tipo_aeronave": request.form["tipo_aeronave"],
            "num_assentos": request.form["num_assentos"]
        }
        current_app.config['VOOS'] = voos
        data.save_voos(voos)
        
        aeroporto1 = voos[voo_id]["origem"]
        aeroporto2 = voos[voo_id]["destino"]
        alterou_coordenadas = False
        
        if aeroporto1 not in coordenadas:
            coordenada = buscar_coordenada(aeroporto1)
            if coordenada:
                coordenadas[aeroporto1] = coordenada
                alterou_coordenadas = True
        if aeroporto2 not in coordenadas:
            coordenada = buscar_coordenada(aeroporto2)
            if coordenada:
                coordenadas[aeroporto2] = coordenada
                alterou_coordenadas = True
        if alterou_coordenadas:
            data.save_coordenadas(coordenadas)
            
        return redirect(url_for('admin.pagina_voos'))

    return render_template('admin/voos_add.html')


@admin_bp.route('/voos/remove/<voo_id>')
@login_required_admin
def delete_voo(voo_id):
    voos = current_app.config.get('VOOS', {})
    if voo_id in voos:
        del voos[voo_id]
        current_app.config['VOOS'] = voos
        data.save_voos(voos)
    return redirect(url_for('admin.pagina_voos'))


@admin_bp.route('/voos/edit/<voo_id>', methods=['GET', 'POST'])
@login_required_admin
def edit_voo(voo_id):
    voos = current_app.config.get('VOOS', {})
    voo = voos.get(voo_id)
    if not voo:
        return redirect(url_for('admin.pagina_voos'))

    if request.method == "POST":
        voos[voo_id] = {
            "codigo": request.form["codigo"],
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": request.form["milhas"],
            "preco_passagem": request.form["preco_passagem"],
            "tipo_aeronave": request.form["tipo_aeronave"],
            "num_assentos": request.form["num_assentos"]
        }
        current_app.config['VOOS'] = voos
        data.save_voos(voos)
        return redirect(url_for('admin.pagina_voos'))

    return render_template('admin/voo_edit.html', voo=voo, voo_id=voo_id)

@admin_bp.route('/reservas')
@login_required_admin
def pagina_reservas():
    reservas_dict = current_app.config.get('RESERVAS', {})

    # Converte o dict em lista, incluindo o ID como campo
    reservas = []
    for reserva_id, dados in reservas_dict.items():
        dados['id'] = reserva_id  # adiciona o ID da reserva ao dict
        reservas.append(dados)

    return render_template("admin/reservas.html", reservas=reservas)
