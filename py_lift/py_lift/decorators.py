def supported_languages(*langs):
    def decorator(cls):
        cls.supported_languages = set(langs)
        return cls
    return decorator