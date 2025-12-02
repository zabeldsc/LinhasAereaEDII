from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import time
from app import data
from app.blueprints.user_bp import login_required_admin
from app.search_structures.arvoreB import ArvoreB
import ast

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
    for cliente in lista_clientes:
        reservas = cliente.get('reservas')
        
        # Se for string (ex: "['123', '456']"), converte para lista real
        if isinstance(reservas, str):
            try:
                # ast.literal_eval converte a string com formato de lista para lista Python
                # Se a string for vazia ou "[]", vira uma lista vazia []
                if not reservas or reservas == "":
                    cliente['reservas'] = []
                else:
                    cliente['reservas'] = ast.literal_eval(reservas)
            except (ValueError, SyntaxError):
                # Se der erro na conversão, assume lista vazia para não quebrar o site
                cliente['reservas'] = []
        
        # Se for None, vira lista vazia
        elif reservas is None:
            cliente['reservas'] = []
            
    cpf_busca = request.args.get('buscar_cpf') or request.form.get('buscar_cpf')    
    clientes_para_exibir = lista_clientes
    
    if cpf_busca:
        arvore = ArvoreB(t=3)
        
        for cliente in lista_clientes:
            cpf = cliente.get('cpf')
            if cpf: 
                arvore.inserir(cpf, cliente)

        resultado = arvore.buscar(cpf_busca)
        
        if resultado:
            clientes_para_exibir = [resultado] # Coloca em lista para o template iterar
            flash(f'Cliente encontrado: {resultado.get("nome")}', 'success')
        else:
            clientes_para_exibir = [] # Lista vazia se não achar
            flash('CPF não encontrado.', 'warning')

    return render_template('admin/clientes.html', clientes=clientes_para_exibir)

@admin_bp.route('/voos/add', methods=['GET', 'POST'])
@login_required_admin
def add_voos():
    if request.method == "POST":
        voos = current_app.config.get('VOOS', {})
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
