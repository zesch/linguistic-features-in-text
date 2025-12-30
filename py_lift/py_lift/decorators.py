def supported_languages(*langs: str):
    def decorator(cls):
        cls.supported_languages = set(langs)
        return cls
    return decorator