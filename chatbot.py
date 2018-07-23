import glob
import json
import pandas as pd
import unicodedata
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer


class Chatbot(object):
    def __init__(self):
        self.iara = ChatBot(
            'Iara',
            logic_adapters=[
                {
                    # A logic adapter that returns a response based on known responses to the closest matches to the input statement.
                    'import_path': 'chatterbot.logic.BestMatch'
                },
                {
                    # Returns a default response with a high confidence when a high confidence response is not known.
                    'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                    'threshold': 0.55,
                    'default_response': 'Desculpa, o que voce disse esta alem da minha compreensao, pode me explicar melhor?'
                }

            ],
            preprocessors=[
                'chatterbot.preprocessors.clean_whitespace'
            ],
            storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
            filters=["chatterbot.filters.RepetitiveResponseFilter"],
            database='iaradb'
        )
        # self.iara.set_trainer(ListTrainer)
        # self.prepare_data()
        self.iara.set_trainer(ChatterBotCorpusTrainer)
        self.iara.train(
            "chatterbot.corpus.portuguese.greetings",
            'conversas',
        )
        self.iara.trainer.export_for_training('./iara.json')


    # eu usei essa funçao p pre processar os dados de backup do facebook pro treino
    def prepare_training_data(self, file):
        with open(file, 'r') as f:
            messages_dict = json.load(f)

        df = pd.DataFrame(messages_dict['messages'])
        df = df[['content', 'sender_name']].fillna('')
        reversed_df = df.iloc[::-1]
        df.head()
        temp = []
        for index, row in reversed_df.iterrows():
            if df['sender_name'][index] == 'Joyce Araujo':
                temp.append(unicodedata.normalize('NFKD', df['content'][index].lower()).encode('ascii', 'ignore').decode())
            else:
                temp.append(unicodedata.normalize('NFKD', df['content'][index].lower()).encode('ascii', 'ignore').decode())
        return temp

    # treina a instancia do chatterbot com as mensagens de backup do facebook
    def prepare_data(self):
        print('#####################preparing facebook data###################')
        for i in range(len(glob.glob1("corpus","*.json"))):
            temp = self.prepare_training_data('corpus/message'+str(i)+'.json')
            self.iara.train(temp)
