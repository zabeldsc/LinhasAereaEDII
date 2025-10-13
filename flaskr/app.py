from flask import Flask, render_template, request, redirect, url_for
import data
import time

app = Flask(__name__)
data.load_voos()

@app.route('/admin/voos')
def pagina_voos():
    return render_template('voos.html',voos=data.voos)

@app.route('/admin/voos/add')
def add_voos():
    return render_template('voos_add.html')

@app.route('/admin/voos/save', methods=['POST'])
def save_voos():
    codigo = request.form["codigo"]
    origem = request.form["origem"]
    destino = request.form["destino"]
    milhas = request.form["milhas"]
    preco_passagem = request.form["preco_passagem"]
    tipo_aeronave = request.form["tipo_aeronave"]
    num_assentos = request.form["num_assentos"]

    voo_id = str(int(time.time()))

    data.voos[voo_id] = {
        "codigo": codigo,
        "origem": origem,
        "destino": destino,
        "milhas": milhas,
        "preco_passagem": preco_passagem,
        "tipo_aeronave": tipo_aeronave,
        "num_assentos": num_assentos
    }

    data.save_voos()

    return redirect(url_for('pagina_voos'))

@app.route('/admin/voos/remove/<voo_id>')
def delete_voo(voo_id):
    if voo_id in data.voos:
        del data.voos[voo_id]

        data.save_voos()
    
    return redirect(url_for('pagina_voos'))

@app.route('/admin/voos/edit<voo_id>/')
def edit_voo(voo_id):
    voo = data.voos.get(voo_id)

    if voo:
        return render_template('voo_edit.html', voo=voo, voo_id=voo_id)
    
@app.route('/admin/voos/update/<voo_id>', methods=['POST'])
def update_voo(voo_id):
    if voo_id in data.voos:
        novo_codigo = request.form["codigo"]
        novo_origem = request.form["origem"]
        novo_destino = request.form["destino"]
        novo_milhas = request.form["milhas"]
        novo_preco_passagem = request.form["preco_passagem"]
        novo_tipo_aeronave = request.form["tipo_aeronave"]
        novo_num_assentos = request.form["num_assentos"]

        data.voos[voo_id] = {
            "codigo": novo_codigo,
            "origem": novo_origem,
            "destino": novo_destino,
            "milhas": novo_milhas,
            "preco_passagem": novo_preco_passagem,
            "tipo_aeronave": novo_tipo_aeronave,
            "num_assentos": novo_num_assentos
        }

        data.save_voos()

    return redirect(url_for('pagina_voos'))



if __name__ == "__main__":
    app.run(debug=True)