import os
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from actions import Action

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    """
    Esse metodo processa as requisiçoes do dialog flow
    """
    req = request.get_json(silent=True, force=True)
    try:
        print("################################REQUISICAO#####################################")
        print(req)
        if req.get('queryResult').get('action') == 'saudacao':
            # saudacao personalizada
            res = act.actionSaudacao(req)
        elif req.get('queryResult').get('action') == 'social':
            # se o dominio da intençao for social retornar resposta do chatterbot
            res = act.get_chatterbot_answer(req)
        else:
            # caso default
            res = act.getAnswer(req)

        print("#################################RESPOSTA####################################")
        print(res)

        return make_response(jsonify(res))


    except AttributeError:
        return 'json error'


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    act = Action()

    app.run(debug=True, port=port, host='0.0.0.0')
