import json
import requests
import constants
from chatbot import Chatbot
from services import db

class Action(object):

    def __init__(self):
        self.bot = Chatbot()
        self.session_ = ''

    # retorna resposta personalizada com o nome do usuario
    def actionSaudacao(self, req):
        output = {}
        username = ''
        output_contexts = req.get('queryResult').get('outputContexts')

        for context in output_contexts:
            # adiciona informaçoes do perfil do usuario no contexto
            if context['name'].endswith('usuario'):
                result = context
                result['parameters'] = self.getUserInfo(output_contexts)
                output['outputContexts'] = [result]
                if result['parameters'] is not None:
                    username = ", " + result['parameters']['first_name']
        output['fulfillmentText'] = "Oi" + username + "! Em que posso ajudar?"
        return output

    # retorna os dados de perfil do usuario baseado no facebook_sender_id
    def getUserInfo(self, contexts):
        facebook_sender_id = None
        if contexts is not None:
            for c in contexts:
                if 'parameters' in c and 'facebook_sender_id' in c['parameters']:
                    facebook_sender_id = c['parameters']['facebook_sender_id']
            if facebook_sender_id is not None:
                request_string = "https://graph.facebook.com/v2.6/" + facebook_sender_id + "?fields=first_name,last_name,gender&access_token=" + constants.PAGE_ACCESS_TOKEN
                result = requests.get(request_string)
                return result.json()
        return None

    # processa o resultado do banco de dados e retorna a resposta no formato adequado
    def processFulfillmentText(self, req, result):
        if result is None:
            result = db.answer.find_one({'action': req.get('queryResult').get('action')})
        resposta = {}
        if result is not None:
            if result.get('followupEvent') is None:
                # processa resposta sem eventos
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
                header = {"Authorization": "Bearer " + constants.CLIENT_ACCESS_TOKEN, "Content-Type": "application/json"}
                url = constants.CONTEXTS_BASE_URL + self.getSessionId(req)
                r = requests.post(str(url), data=json.dumps(aux), headers=header)
                # time.sleep(2)
                # print(aux)
                # print(r)
            else:
                # processa resposta sem eventos
                self.generate_followup_event(req, result)
                # aqui eu preciso preenhcer os parametros do evento
        else:
            resposta['fulfillmentText'] = "Desculpa, o que voce disse esta alem da minha compreensao, pode dizer explicar melhor?"
            # resposta = None
        return resposta

    # processa o resultado do banco de dados e retorna a resposta no formato adequado
    def generate_response_facebook(self, req, result):
        if result is None:
            result = db.answer.find_one({'action': req.get('queryResult').get('action')})
        if result is None:
            result = db.answer.find_one({'action': req.get('queryResult').get('action')})
        resposta = {}
        plataform = 'facebook'
        # print(result)
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
                    resposta = self.processFulfillmentText(req, result)
            else:
                self.generate_followup_event(req, result)
        else:
            resposta = None
        return resposta

    # verifica de onde vem a requisicao e retorna a resposta no formato adequado para cada uma
    def generate_response(self, req, result):
        if result is None:
            result = db.answer.find_one({'action': req.get('queryResult').get('action')})
        plataform = req.get('originalDetectIntentRequest').get('payload').get('source')
        if plataform == 'facebook':
            return self.generate_response_facebook(req, result)
        else:
            return self.processFulfillmentText(req, result)

    # recebe e processa respostas que possuem eventos
    def generate_followup_event(self, req, result):
        event = result.get('followupEvent').get("name")
        if event is not None:
            data = {
                "event": {
                    "name": event
                },
                "lang": "en",
                "sessionId": self.getSessionId(req)
            }
            print('evento')
            print(data)
            header = {"Authorization": "Bearer " + constants.CLIENT_ACCESS_TOKEN, "Content-Type": "application/json"}
            r = requests.post(constants.DIALOGFLOW_BASE_URL, data=json.dumps(data), headers=header)


    # retorna o id da sessao
    def getSessionId(self, req):
        return req.get('session').rsplit('/', 1)[-1]

    # verifica se a sessao mudou
    def compare_session(self, req):
        if self.session_ == self.getSessionId(req):
            return True
        else:
            return False

    # zera o lifespan dos  contextos atuais
    def reset_contexts(self, data):
        header = {"Authorization": "Bearer " + constants.CLIENT_ACCESS_TOKEN, "Content-Type": "application/json"}
        r = requests.post(constants.DIALOGFLOW_BASE_URL, data=json.dumps(data), headers=header)


    # essa funçao recebe uma requisiçao e retorna a resposta cadastrada no banco para os parametros da req
    def getAnswer(self, req):
        parameters = req.get('queryResult').get('parameters').keys()
        temp2 = []
        # cada parametro da intençao identificada corresponde a um filtro da query
        for param_name in parameters:
            aux = req.get('queryResult').get('parameters')[param_name]
            temp = {}
            if aux is not None:
                temp[param_name] = {"$eq": aux }
            temp2.append(temp)
        temp={}
        temp['action'] = req.get('queryResult').get('action')
        temp2.append(temp)
        # encontrar resposta para a action no banco
        result = db.answer.find({"$and":temp2})
        if result.count() > 0:
            result = result[0]
            print("#################################RESULTADO DO BANCO####################################")
            print(result)
        else:
            result = {"fulfillmentText": "Desculpe, nao possuo essa informaçao"}
        return self.generate_response(req, result)

    # Return a response based on a given input statement.
    def get_chatterbot_answer(self, req):
        res_iara = self.bot.iara.get_response(req.get('queryResult').get('queryText'))
        print("#################################RESPOSTA IARA####################################")
        print(res_iara)
        res = {
            'fulfillmentText': str(res_iara)
        }
        return res
