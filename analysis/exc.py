

class WindRuntimeError(BaseException):
    def __init__(self, error_no: int):
        self.error_no = error_no

    def __repr__(self):
        return f'Wind运行时错误，错误码 {self.error_no}'
