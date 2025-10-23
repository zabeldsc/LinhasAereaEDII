from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session
import time
from app import data

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_user' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
def raiz():
    return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == "POST":
        user_keys = current_app.config.get('USER_KEYS', {})
        user = request.form["usuario"]
        pw = request.form["senha"]

        if user not in user_keys:
            erro = "Usuário não encontrado"
        elif pw != user_keys[user]["senha"]:
            erro = "Senha incorreta"
        else:
            # Marca como logado
            session['admin_user'] = user
            return redirect(url_for('admin.pagina_voos'))

    return render_template('admin/login.html', erro=erro)


@admin_bp.route('/voos')
@login_required
def pagina_voos():
    voos = current_app.config.get('VOOS', {})
    return render_template('admin/voos.html', voos=voos)


@admin_bp.route('/voos/add', methods=['GET', 'POST'])
@login_required
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
@login_required
def delete_voo(voo_id):
    voos = current_app.config.get('VOOS', {})
    if voo_id in voos:
        del voos[voo_id]
        current_app.config['VOOS'] = voos
        data.save_voos(voos)
    return redirect(url_for('admin.pagina_voos'))


@admin_bp.route('/voos/edit/<voo_id>', methods=['GET', 'POST'])
@login_required
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

@admin_bp.route('/logout')
@login_required
def logout():
    session.pop('admin_user', None)
    return redirect(url_for('passageiro.pagina_inicial'))
