import json
import requests
import config
from bson.json_util import dumps

from services import db


def actionEstSupSobre(req):
    resposta = {}
    result = db.answers.find_one({'action': req.get('queryResult').get('action')})
    if result is not None:
        resposta['fulfillmentText'] = result['fulfillmentText']
    return resposta


def actionHorarioSecretaria(req):
    return db.answers.find_one({'action': 'horariosecretaria'})

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
            request_string = "https://graph.facebook.com/v2.6/" + facebook_sender_id +"?fields=first_name,last_name,gender&access_token=" + config.PAGE_ACCESS_TOKEN
            result = requests.get(request_string)
            return result.json()
    return None


def actionProfDisc(req):
    result = db.answers.find_one({'action': req.get('queryResult').get('action')})
    resposta = {}
    disciplina = req.get('queryResult').get('parameters').get('disciplina')
    if disciplina is not None:
        resposta['fulfillmentText'] = result['fulfillmentText'].replace('<DISCIPLINA>', disciplina)
    return resposta

def actionCoordCurso(req):

    if req.get('queryResult').get('allRequiredParamsPresent') is not None and req.get('queryResult').get('allRequiredParamsPresent')== True:
        resposta = {}
        curso = req.get('queryResult').get('parameters')['curso']
        plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
        result = db.answers.find({
            'action': req.get('queryResult').get('action'),
            'curso': curso,
        })[0]
        if plataform != '':
            resposta['payload'] = result.get('payload')
            for param in result['parameters']:
                print(param)
                resposta['payload'][plataform]['text'] = resposta['payload'][plataform]['text'].replace('<param>', result[param], 1)
        else:
            resposta['fulfillmentText'] = result.get('fulfillmentText')

    return resposta