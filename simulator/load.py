import json

class Loader:
    @staticmethod
    def load(jsonFilePath):
        with open(jsonFilePath, 'r') as json_file:
            data = json.load(json_file)
        return data