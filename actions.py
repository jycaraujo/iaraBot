import json
import requests
import config
from services import db

session_ = ''

def actionSaudacao(req):
    output = {}
    username = ''
    output_contexts = req.get('queryResult').get('outputContexts')

    for context in output_contexts:
        if context['name'].endswith('usuario'):
            result = context
            result['parameters'] = getUserInfo(output_contexts)
            output['outputContexts'] = [result]
            if result['parameters'] is not None:
                username = ", " + result['parameters']['first_name']

    output['fulfillmentText'] = "Oi" + username + "! Em que posso ajudar?"
    return output


def getUserInfo(contexts):
    facebook_sender_id = None
    if contexts is not None:
        for c in contexts:
            if 'parameters' in c and 'facebook_sender_id' in c['parameters']:
                facebook_sender_id = c['parameters']['facebook_sender_id']
        if facebook_sender_id is not None:
            request_string = "https://graph.facebook.com/v2.6/" + facebook_sender_id + "?fields=first_name,last_name,gender&access_token=" + config.PAGE_ACCESS_TOKEN
            result = requests.get(request_string)
            return result.json()
    return None
#
#
# def actionCoordCurso(req):
#     return getAnswer(req, ['curso'])

def processFulfillmentText(req, result):
    if result is None:
        result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    resposta = {}
    if result is not None:
        if result.get('followupEvent') is None:
            aux = []
            if result.get('fulfillmentText') is not None:
                resposta['fulfillmentText'] = result.get('fulfillmentText')
                if result.get('parameters') is not None:
                    temp = {}
                    temp['outputContexts'] = req.get('queryResult').get('outputContexts')
                    for param in result['parameters']:
                        if param in result:
                            resposta['fulfillmentText'] = resposta['fulfillmentText'].replace('<param>', result[param],
                                                                                              1)
                            if temp['outputContexts'] is not None:
                                for context in temp['outputContexts']:
                                    context['parameters'][param] = result[param]
                                    context['parameters'][str(param + '.original')] = result[param]
                                    aux.append(context)
                            # else:
                            #     resposta['fulfillmentText'] = 'Desculpa, nao possuo essa informaçao'
                    if len(aux) > 0:
                        resposta['outputContexts'] = aux
                        # resposta = None
            print(resposta)
            header = {"Authorization": "Bearer " + config.CLIENT_ACCESS_TOKEN, "Content-Type": "application/json"}
            url = config.CONTEXTS_BASE_URL + getSessionId(req)
            r = requests.post(str(url), data=json.dumps(aux), headers=header)
            print(aux)
            print(r)
        else:
            generate_followup_event(req, result)
            # resposta['']
            # aqui eu preciso preenhcer os parametros do evento
    else:
        # resposta['fulfillmentText'] = "Desculpa, nao entendi o que vc quer, pode dizer explicar melhor?"
        resposta = None
    return resposta

def generate_response_facebook(req, result):
    if result is None:
        result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    if result is None:
        result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    resposta = {}
    plataform = 'facebook'
    print(result)
    if result is not None:
        if result.get('followupEvent') is None:
            aux = []
            if plataform is not None and result.get('payload') is not None and result.get('payload').get(
                    plataform) is not None and result.get('payload').get(plataform).get('text') != '':
                resposta['payload'] = result.get('payload')
                if result.get('parameters') is not None:
                    temp = {}
                    temp['outputContexts'] = req.get('queryResult').get('outputContexts')
                    for param in result['parameters']:
                        if param in result:
                            resposta['payload'][plataform]['text'] = resposta['payload'][plataform]['text'].replace(
                                '<param>',
                                result[
                                    param],
                                1)
                            if temp['outputContexts'] is not None:
                                for context in temp['outputContexts']:
                                    context['parameters'][param] = result[param]
                                    context['parameters'][str(param + '.original')] = result[param]
                                    aux.append(context)
            elif result.get('fulfillmentText') is not None:
                resposta = processFulfillmentText(req, result)
        else:
            generate_followup_event(req, result)
    else:
        resposta = None
    return resposta

def generate_response(req, result):
    if result is None:
        result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
    if plataform == 'facebook':
        return generate_response_facebook(req, result)
    else:
        return processFulfillmentText(req, result)


def generate_followup_event(req, result):
    event = result.get('followupEvent').get("name")
    if event is not None:
        data = {
            "event": {
                "name": event,
                # "data": {
                #     "docente-nome": "Ivan"
                # }
            },
            "lang": "en",
            "sessionId": getSessionId(req)
        }
        header = {"Authorization": "Bearer " + config.CLIENT_ACCESS_TOKEN, "Content-Type": "application/json"}
        r = requests.post(config.DIALOGFLOW_BASE_URL, data=json.dumps(data), headers=header)
        print(data)
        print(r)


def getSessionId(req):
    return req.get('session').rsplit('/', 1)[-1]


def compare_session(req):
    if session_ == getSessionId(req):
        return True
    else:
        return False

def reset_contexts(data):
    header = {"Authorization": "Bearer " + config.CLIENT_ACCESS_TOKEN, "Content-Type": "application/json"}
    r = requests.post(config.DIALOGFLOW_BASE_URL, data=json.dumps(data), headers=header)
    print(r)

#
# def actionPreReq(req):
#     return getAnswer(req, ['disciplina'])
#
#
# def actionLugarHorario(req):
#     return getAnswer(req, ['lugar'])

def getAnswer(req):
    temp = {}
    parameters = req.get('queryResult').get('parameters').keys()
    for param_name in parameters:
        aux = req.get('queryResult').get('parameters')[param_name]
        if aux is not None:
            temp[param_name] = aux
    temp['action'] = req.get('queryResult').get('action')
    print(temp)
    result = db.answer.find({"$and":[temp]})
    if result.count() > 0:
        result = result[0]
        print(result)
    else:
        result = None
    return generate_response(req, result)

