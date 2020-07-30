''' Module for generic file parser '''

class Parser:
    ''' implements methods for iterable objects '''

    def __init__(self, file, buffer):
        self.file = open(file, 'rb')
        self.buffer = buffer
        self.is_closed = False

    def __iter__(self):
        return self

    def __next__(self):
        return self._next()

    def __del__(self):
        self._del()

    def _next(self):
        if self.is_closed:
            raise StopIteration()
        out = self.file.read(self.buffer)
        if out == b'':
            self._del()
            raise StopIteration()
        return out.decode()

    def _del(self):
        self.is_closed = True
        self.file.close()