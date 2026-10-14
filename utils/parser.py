import json


def parse_input(input_data):

    if isinstance(input_data, str):
        return json.loads(input_data)

    return input_data