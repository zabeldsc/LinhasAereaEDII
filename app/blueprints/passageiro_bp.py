from flask import Blueprint, redirect, render_template, current_app, request, url_for

passageiro_bp = Blueprint('passageiro', __name__, url_prefix='/passageiro')

@passageiro_bp.route('/')
def pagina_inicial():
    voos = current_app.config.get('VOOS', {})
    return render_template('passageiro/pagina_inicial.html', voos=voos)

# Rota de login do passageiro
@passageiro_bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        # Pega os dados de usuários do passageiro (USER_KEYS do app)
        user_keys = current_app.config.get('USER_KEYS', {})
        user = request.form['usuario']
        pw = request.form['senha']

        if user not in user_keys:
            erro = "Usuário não encontrado"
        elif pw != user_keys[user]["senha"]:
            erro = "Senha incorreta"
        else:
            # Login bem-sucedido: redireciona para a página de reservas/compras
            return redirect(url_for('passageiro.reservas'))

    # Renderiza o template de login, passando qualquer erro
    return render_template('passageiro/login.html', erro=erro)