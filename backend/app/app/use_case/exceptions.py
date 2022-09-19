class BaseUseCaseException(Exception):
    pass

class NoSuchObject(BaseUseCaseException):
    pass

class ObjectAlreadyExists(BaseUseCaseException):
    pass

class DoneWithErrors(BaseUseCaseException):
    pass

class FailedToParseACLRule(BaseUseCaseException):
    pass

class FailedToParseACLSymbols(FailedToParseACLRule):
    pass

class FailedToParseTextPrivileges(FailedToParseACLRule):
    pass

class TypeNotImplemented(FailedToParseACLRule):
    pass