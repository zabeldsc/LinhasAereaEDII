from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app import data

user_bp = Blueprint('user', __name__, url_prefix='/user')

# ----------------------
# Página inicial
# ----------------------
@user_bp.route('/')
def pagina_inicial():
    voos = current_app.config.get('VOOS', {})
    return render_template('user/pagina_inicial.html', voos=voos)

# ----------------------
# Decoradores de login
# ----------------------
def login_required_passageiro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session or session.get('tipo') != 'passageiro':
            flash('Você precisa fazer login como passageiro.', 'error')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return wrapper


def login_required_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session or session.get('tipo') != 'admin':
            flash('Acesso permitido apenas para administradores.', 'error')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return wrapper

# ----------------------
# LOGIN
# ----------------------
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form.get('email')
        senha = request.form.get('senha')

        adm_keys = current_app.config.get('ADM_KEYS', {})

        if email in adm_keys and adm_keys[email]['senha'] == senha:
            session['usuario'] = email
            session['nome'] = adm_keys[email].get('nome', email)
            session['tipo'] = 'admin'

            flash(f"Bem-vindo, {session['nome']}!", "success")
            return redirect(url_for('admin.pagina_voos'))

        clientes = data.load_clientes()
        passageiro = next((c for c in clientes if c["email"] == email and c["senha"] == senha), None)

        if passageiro:
            session['usuario'] = email
            session['nome'] = passageiro["nome"]
            session['tipo'] = "passageiro"

            flash(f"Bem-vindo, {session['nome']}!", "success")
            return redirect(url_for('passageiro.dashboard'))

        flash("Email ou senha incorretos.", "error")

    return render_template("user/login.html")

# ----------------------
# LOGOUT
# ----------------------
@user_bp.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da conta com sucesso!", "success")
    return redirect(url_for('user.pagina_inicial'))

# ----------------------
# CADASTRO (somente PASSAGEIRO)
# ----------------------
@user_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':

        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        cpf = request.form.get('cpf')

        adm_keys = current_app.config.get('ADM_KEYS', {})
        if email in adm_keys:
            flash("Este email pertence a um administrador. Use outro.", "error")
            return redirect(url_for('user.cadastro'))

        clientes = data.load_clientes()

        if any(c['email'] == email for c in clientes):
            flash("Email já cadastrado!", "error")
            return redirect(url_for('user.cadastro'))

        clientes.append({
            "cpf": cpf,
            "nome": nome,
            "email": email,
            "senha": senha,
            "milhas": "0",
            "reservas": []
        })

        data.save_clientes(clientes)

        session['usuario'] = email
        session['nome'] = nome
        session['tipo'] = 'passageiro'

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('passageiro.dashboard'))

    return render_template('user/cadastro.html')