import pprint
import os
from flask import current_app


class AdditionalFunctions:

    def view_dict(self, obj):
        print('--------------')
        print('Type:', obj.__class__)
        d = obj.__dict__
        pprint.pprint(d)
        return d

    def get_default_directory(self):
        return os.path.join(current_app.root_path)

    def xor(self, x, y):
        return bytes(x[i] ^ y[i] for i in range(min(len(x), len(y))))