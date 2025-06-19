class JsonStorageService:
    def __init__(self, base_path: str,):
        
        self.base_path = base_path

    def save(self, file_name: str, data):
        import json
        with open(f"{self.base_path}/{file_name}", 'w') as file:
            json.dump(data, file)
    

    def load(self, file_name: str):
        import json
        try:
            with open(f"{self.base_path}/{file_name}", 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None
    