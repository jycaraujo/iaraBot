import json
import requests
import config
from bson.json_util import dumps

from services import db


def actionEstSupSobre(req):
    resposta = {}
    result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    if result is not None:
        resposta['fulfillmentText'] = result['fulfillmentText']
    return resposta


def actionHorarioSecretaria(req):
    return db.answer.find_one({'action': 'horariosecretaria'})


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

    output['fulfillmentText'] = "Oi" + username + "! Tudo bem?"
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


def actionProfDisc(req):
    result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    resposta = {}
    # se existe evento pula tudo
    if result.get('events') is not None:
        resposta['events'] = result.get('events')
    else:
        # se existe payload a resposta eh por payload
        if result['payload'] is not None:
            plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
            if plataform != '' and result['payload'][plataform]['text'] != '':
                resposta['payload'] = result['payload'][plataform]['text']
                # daih pra cada parametro que estiver no banco de dados eu substituo o valor dele na frase de resposta
                for p in result.get('parameters'):
                    param = req.get('queryResult').get('parameters').get(p)
                    if param is not None:
                        resposta['payload'] = resposta['payload'].replace('<param>', param)
        # senao eh a resposta comum mesmo
        else:
            resposta['fulfillmentText'] = result['fulfillmentText']
            # daih pra cada parametro que estiver no banco de dados eu substituo o valor dele na frase de resposta
            for p in result.get('parameters'):
                param = req.get('queryResult').get('parameters').get(p)
                if param is not None:
                    resposta['fulfillmentText'] = result['fulfillmentText'].replace('<param>', param)

    return resposta


def actionCoordCurso(req):
    resposta = {}
    curso = req.get('queryResult').get('parameters')['curso']
    result = db.answer.find({
        'action': req.get('queryResult').get('action'),
        'curso': curso,
    })[0]
    if result['payload'] is not None:
        plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
        if plataform != '' and result['payload'][plataform]['text'] != '':
            resposta['payload'] = result.get('payload')
            if result.get('parameters') is not None:
                for param in result['parameters']:
                    resposta['payload'][plataform]['text'] = resposta['payload'][plataform]['text'].replace('<param>',
                                                                                                            result[
                                                                                                                param],
                                                                                                            1)
    else:
        if result.get('fulfillmentText') is not None:
            resposta['fulfillmentText'] = result.get('fulfillmentText')


    return resposta


def actionSobreDocente(req):
    print('sobre docente')
    return {}


def actionCoordCursoMais(req):
    resposta = {}
    result = db.answer.find_one({'action': req.get('queryResult').get('action')})
    if result.get('followupEvent') is None:
        plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
        if plataform != '':
            resposta['payload'] = result.get('payload')
            if result.get('parameters') is not None:
                for param in result['parameters']:
                    resposta['payload'][plataform]['text'] = resposta['payload'][plataform]['text'].replace('<param>',
                                                                                                            result[
                                                                                                                param],
                                                                                                            1)
        else:
            if result.get('fulfillmentText') is not None:
                resposta['fulfillmentText'] = result.get('fulfillmentText')
    else:
        resposta['followupEvent'] = result.get('followupEvent')
    return resposta
