class Response:
    def __init__(self, *args, indexed=False):
        self.args = args
        self.indexed = indexed

    def __repr__(self):
        res = ''
        for i, j in enumerate(self.args, start=1):
            if self.indexed:
                res += f'{i}. {j}\n'
            else:
                res += f'{j}\n'
        return res
