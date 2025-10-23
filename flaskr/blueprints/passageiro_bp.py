import flask
import data

passageiro_bp = flask.Blueprint('passageiro', __name__, url_prefix='/passageiro')

@passageiro_bp.route('/')
def pagina_inicial():
    return flask.render_template('passageiro/pagina_inicial.html', voos=data.voos)
