"""Custom exceptions for the lti_toolbox app."""


class LTIException(Exception):
    """Custom LTI exception for proper handling of LTI specific errors."""


class LTIRequestNotVerifiedException(LTIException):
    """
    Custom LTI exception thrown when someone tries to access
    LTI parameters before verifying the request.
    """

    def __init__(self):
        message = "You must verify the LTI request with verify() before accessing its parameters"
        super().__init__(message)


class ParamException(Exception):
    """Custom Exception related to LTI param processing."""


class InvalidParamException(ParamException):
    """Custom Exception thrown when an invalid parameter is found in an LTI request."""

    def __init__(self, param):
        message = f"{param:s} is not a valid param"
        super().__init__(message)


class MissingParamException(ParamException):
    """
    Custom Exception thrown when a required LTI parameter is missing in
    an LTI request.
    """

    def __init__(self, param):
        message = f"missing param : {param:s}"
        super().__init__(message)
