import json

class Loader:
    def load(self, jsonFilePath):
        with open(jsonFilePath, 'r') as json_file:
            data = json.load(json_file)
        return data