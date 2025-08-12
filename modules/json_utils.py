import json


class JsonUtils:

    @staticmethod
    def save_list_to_json(data_list, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=2)


    @staticmethod
    def append_list_to_json(new_items, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.extend(new_items)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


    @staticmethod
    def load_json(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
