def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def endpoint(method, endpoint_path, token_required=True):
    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            if token_required:
                self.authenticate()
            kwargs.update(dict(method=method,
                               endpoint_path=endpoint_path))
            return f(self, *args, **kwargs)
        return wrapped_f
    return wrap
