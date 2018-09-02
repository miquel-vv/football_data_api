import json
from os import path


def get_sample_data(data):
    """Return test JSON payload as 'json' object."""
    _path = path.join(
        path.abspath(path.dirname(__file__)),
        'sample_data\\{}.json'.format(data)
    )
    with open(_path, 'r') as f:
        return json.load(f)
