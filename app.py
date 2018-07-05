import os
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request

import actions as act

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    """
        This method handles the http requests for the Dialogflow webhook
        This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    res = ""
    try:
        print(req)

        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    if action == 'horario-secretaria':
        res = act.actionHorarioSecretaria(req)
    elif action == 'estagio-supervisionado.sobre':
        res = act.actionEstSupSobre(req)
    elif action == 'saudacao':
        res = act.actionSaudacao(req)
    elif action == 'coordenador-curso':
        res = act.actionCoordCurso(req)
    elif action == 'coordenador-curso.sabermais':
        res = act.actionCoordCursoMais(req)
    elif action == 'sobre-docente':
        res = act.actionSobreDocente(req)
    #
    print(str(res))

    return make_response(jsonify(res))


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
