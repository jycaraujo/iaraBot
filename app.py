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
        # print(act.getSessionId(req))
        # print(session_)
        # print(req)
        res = {}
        # if act.compare_session(req):
        #     print('same session')
        #     res = process_request(req)
        #     print(res)
        #     if res is None:
        #         res_iara = bot.iara.get_response(req.get('queryResult').get('queryText'))
        #         print(res_iara)
        #         # res = {}
        #         res = {
        #             'fulfillmentText': str(res_iara)
        #         }
        # else:
        #     res = {
        #         "resetContexts": True,
        #         "query": req.get('queryResult').get('queryText'),
        #         "lang": "en",
        #         "sessionId": act.getSessionId(req)
        #     }
        #     session_ =   act.getSessionId(req)
        #     act.reset_contexts(res)
        # # print(res)
        res = process_request(req)
        print(res)
        if res is None:
            res_iara = bot.iara.get_response(req.get('queryResult').get('queryText'))
            print(res_iara)
            # res = {}
            res = {
                'fulfillmentText': str(res_iara)
            }

        return make_response(jsonify(res))


    except AttributeError:
        return 'json error'




def process_request(req):
    res = ""
    action = req.get('queryResult').get('action')
    if action == 'saudacao':
        res = act.actionSaudacao(req)
    elif action == 'coordenador-curso':
        res = act.actionCoordCurso(req)
    elif action == 'prerequisito':
        res = act.actionPreReq(req)
    else:
        plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
        if plataform == 'facebook':
            res = act.generate_response_facebook(req, None)
        else:
            res = act.generate_response(req, None)
    return res

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    bot = Chatbot()
    session_ = ''

    app.run(debug=True, port=port, host='0.0.0.0')
