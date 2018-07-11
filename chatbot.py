import glob
import json

import pandas as pd
import unicodedata
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer


class Chatbot(object):
    def __init__(self):
        print('new chatot')
        self.iara = ChatBot(
            'Iara',
            logic_adapters=[
                'chatterbot.logic.BestMatch'
            ],
            storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
            filters=["chatterbot.filters.RepetitiveResponseFilter"]
            # database='iaradb'
        )
        # self.iara.set_trainer(ListTrainer)
        # self.prepare_data()
        self.iara.set_trainer(ChatterBotCorpusTrainer)
        self.iara.train(
            "chatterbot.corpus.portuguese",
            # data
        )
        self.iara.trainer.export_for_training('./iara.json')


    def prepare_training_data(self, file):
        with open(file, 'r') as f:
            messages_dict = json.load(f)

        df = pd.DataFrame(messages_dict['messages'])
        df = df[['content', 'sender_name']].fillna('')
        reversed_df = df.iloc[::-1]
        df.head()
        temp = []
        for index, row in reversed_df.iterrows():
            #     print(df['sender_name'])
            if df['sender_name'][index] == 'Joyce Araujo':
                temp.append(unicodedata.normalize('NFKD', df['content'][index].lower()).encode('ascii', 'ignore').decode())
            else:
                temp.append(unicodedata.normalize('NFKD', df['content'][index].lower()).encode('ascii', 'ignore').decode())
        return temp

    def prepare_data(self):
        print('prepare data')
        temp = []
        print(len(glob.glob1("dataset", "*.json")))
        for i in range(len(glob.glob1("dataset","*.json"))):
            print(str(i))
            temp = self.prepare_training_data('dataset/message'+str(i)+'.json')

        self.iara.train(temp)