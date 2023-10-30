import json

class Loader:
    def load_model(self, jsonFilePath):
        with open(jsonFilePath, 'r') as json_file:
            model_data = json.load(json_file)
        return model_data