from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app import data

user_bp = Blueprint('user', __name__, url_prefix='/user')

# ----------------------
# Rota inicial
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
            flash('É necessário fazer login como passageiro.', 'error')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return wrapper

def login_required_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario' not in session or session.get('tipo') != 'admin':
            flash('É necessário fazer login como administrador.', 'error')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return wrapper

# ----------------------
# Login
# ----------------------
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_form = request.form.get('email')
        senha_form = request.form.get('senha')
        usuarios = current_app.config.get('USER_KEYS', {})

        if email_form in usuarios and usuarios[email_form]['senha'] == senha_form:
            tipo = usuarios[email_form]['tipo']
            nome = usuarios[email_form].get('nome', email_form)

            # Sessão
            session['usuario'] = email_form
            session['nome'] = nome
            session['tipo'] = tipo

            flash(f'Bem-vindo, {nome}!', 'success')

            if tipo == 'admin':
                return redirect(url_for('admin.pagina_voos'))
            else:
                return redirect(url_for('passageiro.dashboard'))
        else:
            flash('Email ou senha incorretos.', 'error')

    return render_template('user/login.html')

# ----------------------
# Logout
# ----------------------
@user_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta com sucesso!', 'success')
    return redirect(url_for('user.pagina_inicial'))

# ----------------------
# Cadastro
# ----------------------
@user_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        user_keys = current_app.config.get('USER_KEYS', {})

        if email in user_keys:
            flash('Email já cadastrado!', 'error')
        else:
            # Cria novo usuário tipo passageiro
            user_keys[email] = {
                'senha': senha,
                'tipo': 'passageiro',
                'nome': nome
            }

            # Atualiza o config e salva no JSON
            current_app.config['USER_KEYS'] = user_keys
            data.save_user_keys(user_keys)

            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('user.login'))

    return render_template('user/cadastro.html')