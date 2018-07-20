import os
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request

import actions as act
from chatbot import Chatbot

session_ = ''
app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    """
        This method handles the http requests for the Dialogflow webhook
        This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    try:
        print("################################REQUISICAO#####################################")
        print(req)
        if req.get('queryResult').get('action') == 'saudacao':
            res = act.actionSaudacao(req)
        elif req.get('queryResult').get('action') is None:
            res_iara = bot.iara.get_response(req.get('queryResult').get('queryText'))
            print("#################################RESPOSTA IARA####################################")
            print(res_iara)
            res = {
                'fulfillmentText': str(res_iara)
            }
        else:
            res = act.getAnswer(req)

        print("#################################RESPOSTA####################################")
        print(res)

        return make_response(jsonify(res))


    except AttributeError:
        return 'json error'


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    bot = Chatbot()
    session_ = ''

    app.run(debug=True, port=port, host='0.0.0.0')
