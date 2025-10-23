import flask
from blueprints.admin_bp import admin_bp
from blueprints.passageiro_bp import passageiro_bp
import data

app = flask.Flask(__name__)
data.load_voos()

# Registrar Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(passageiro_bp)

# Rota raiz simples
@app.route('/')
def raiz():
    return flask.redirect(flask.url_for('passageiro.pagina_inicial'))

if __name__ == "__main__":
    app.run(debug=True)
