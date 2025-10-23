from flask import Blueprint, render_template, request, redirect, url_for
import data, time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def raiz():
    return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == "POST":
        data.load_user_keys()
        user = request.form["usuario"]
        pw = request.form["senha"]

        if user not in data.user_keys:
            erro = "Usuário não encontrado"
        elif pw != data.user_keys[user]["senha"]:
            erro = "Senha incorreta"
        else:
            # login bem-sucedido
            return redirect(url_for('admin.pagina_voos'))

    return render_template('admin/login.html', erro=erro)

@admin_bp.route('/voos')
def pagina_voos():
    return render_template('admin/voos.html', voos=data.voos)

# CRUD dos voos
@admin_bp.route('/voos/add', methods=['GET', 'POST'])
def add_voos():
    if request.method == "POST":
        voo_id = str(int(time.time()))
        data.voos[voo_id] = {
            "codigo": request.form["codigo"],
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": request.form["milhas"],
            "preco_passagem": request.form["preco_passagem"],
            "tipo_aeronave": request.form["tipo_aeronave"],
            "num_assentos": request.form["num_assentos"]
        }
        data.save_voos()
        return redirect(url_for('admin.pagina_voos'))
    return render_template('admin/voos_add.html')

@admin_bp.route('/voos/remove/<voo_id>')
def delete_voo(voo_id):
    if voo_id in data.voos:
        del data.voos[voo_id]
        data.save_voos()
    return redirect(url_for('admin.pagina_voos'))

@admin_bp.route('/voos/edit/<voo_id>', methods=['GET', 'POST'])
def edit_voo(voo_id):
    voo = data.voos.get(voo_id)
    if request.method == "POST":
        data.voos[voo_id] = {
            "codigo": request.form["codigo"],
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": request.form["milhas"],
            "preco_passagem": request.form["preco_passagem"],
            "tipo_aeronave": request.form["tipo_aeronave"],
            "num_assentos": request.form["num_assentos"]
        }
        data.save_voos()
        return redirect(url_for('admin.pagina_voos'))
    return render_template('admin/voo_edit.html', voo=voo, voo_id=voo_id)
