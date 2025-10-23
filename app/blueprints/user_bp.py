from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

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
        usuario_form = request.form.get('usuario')
        senha_form = request.form.get('senha')
        usuarios = current_app.config.get('USER_KEYS', {})

        if usuario_form in usuarios and usuarios[usuario_form]['senha'] == senha_form:
            tipo = usuarios[usuario_form]['tipo']
            session['usuario'] = usuario_form
            session['tipo'] = tipo

            flash(f'Bem-vindo, {usuario_form}!', 'success')

            if tipo == 'admin':
                return redirect(url_for('admin.pagina_voos')) 
            else:
                return redirect(url_for('passageiro.dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'error')

    return render_template('user/login.html')

# ----------------------
# Logout
# ----------------------
@user_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta com sucesso!', 'success')
    return redirect(url_for('user.pagina_inicial'))
