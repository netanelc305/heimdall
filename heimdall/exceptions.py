class HeimdallException(Exception):
    """Base class for all exceptions related to Heimdall."""
    pass


class VolatilitySymbols(HeimdallException):
    """Base class for exceptions related to profiles."""

    def __init__(self, name=''):
        super().__init__()
        self.name = name


class SymbolsFileNotFoundError(VolatilitySymbols):
    """Raised when a specified symbols file is not found."""
    pass


class SymbolsFileRemoteNotFoundError(VolatilitySymbols):
    """Raised when a specified symbols file is not found on the remote repository."""
    pass


class SymbolsFileFormatError(VolatilitySymbols):
    """Raised when a specified symbols file not properly formatted."""
    pass


class ConnectionFailedError(HeimdallException):
    """Raised when a connection to the virtual machine fails."""
    pass


class AccessDeniedError(HeimdallException):
    """Need extra permissions to execute this command."""
    pass
