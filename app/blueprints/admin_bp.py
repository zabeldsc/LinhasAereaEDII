from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
import time
from app import data
from app.blueprints.user_bp import login_required_admin

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/voos')
@login_required_admin
def pagina_voos():
    voos = current_app.config.get('VOOS', {})
    return render_template('admin/voos.html', voos=voos)

@admin_bp.route('/clientes')
@login_required_admin
def pagina_clientes():
    clientes = current_app.config.get('CLIENTES', {})
    return render_template('admin/clientes.html', clientes=clientes)

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
        current_app.config['VOOS'] = voos  # Atualiza o config
        data.save_voos(voos)  # Salva no JSON
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