# pylint: disable=invalid-name
"""
    class PredictResponse untuk mendapatkan prediksi intent dari suatu text
"""

import torch
from classes.NeuralNet import NeuralNet
from classes.PreProses import PreProses

class PredictResponse:
    """
        kelas PredictResponse
    """

    def __init__(self, model_folder):
        self.model_folder = model_folder
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dir = f'model/{self.model_folder}'
        self.model_path = f'{self.dir}/data.pth'
        self.pre_proses = PreProses(self.model_folder)

    def get_data_model(self):
        """
            mendapatkan data model 
        """

        # return torch.load(self.model_path)
        return torch.load(self.model_path, map_location=torch.device('cpu'))


    def predict(self, sentence):
        """
            memprediksi text yang diinput termasuk dalam kelas atau keyword apa
        """
        # pylint: disable=invalid-name

        data = self.get_data_model()

        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size = data["output_size"]
        all_words = data['all_words']
        tags = data['tags']
        model_state = data["model_state"]

        model = NeuralNet(input_size, hidden_size, output_size).to(self.device)
        model.load_state_dict(model_state)
        model.eval()

        sentence = self.pre_proses.tokenizing(sentence)
        X = self.pre_proses.bag_of_words(sentence, all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(self.device)

        output = model(X)
        _, predicted = torch.max(output, dim=1)

        tag = tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        return tag, prob

    def get_response(self, predict):
        """
            mendapatkan response dari intent hasil predict
        """

        return self.get_by_id(predict[0])


    def get_by_id(self, id):
        """
            mendapatkan intent berdasarkan tag
        """

        intents = self.pre_proses.get_intents()
        for intent in intents.get('intents'):
            if id == intent.get('id'):
                return intent

        return {
                'id': None,
                'patterns': None
            }
        