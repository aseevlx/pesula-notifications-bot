class NortecApiApplicationException(ValueError):
    def __init__(self, message: str = "Illegal application name"):
        super().__init__(message)


class NortecApiServerException(ValueError):
    def __init__(self, message: str = "Unhandled server error"):
        super().__init__(message)


class NortecApiCorruptedSessionException(ValueError):
    def __init__(self, message: str = "Session string corrupt"):
        super().__init__(message)


class NortecApiSessionExpiredException(ValueError):
    def __init__(self, message: str = "Session string expired"):
        super().__init__(message)


class NortecApiLogicException(ValueError):
    def __init__(self, message: str):
        super().__init__(message)
