import json
from enum import Enum
from pathlib import Path
from typing import Any, Union

from heimdall.exceptions import SymbolsFileFormatError


class OSType(Enum):
    MACOS = 1
    WINDOWS = 2
    LINUX = 3


class ISFFile:
    """
    Manages and accesses symbol information from a JSON file in ISF (Intermediate Symbol File) format.

    The `ISFFile` class provides methods to load and interact with symbol data extracted from a JSON file,
    typically used in volatility frameworks for memory forensics. It allows retrieval of types, symbols,
    enums, and metadata about the operating system.
    """

    def __init__(self, path: Path) -> None:
        """
        Initialize the ISFFile by loading data from the given JSON file.

        Parameters
        ----------
        path : str
            The file path to the ISF JSON file.

        Raises
        ------
        SymbolsFileFormatError
            If the JSON file cannot be loaded or is missing required keys.
        """
        self.path: Path = path
        try:
            with open(path, 'r') as f:
                self.data: dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise SymbolsFileFormatError(f"Failed to load ISF file: {e}")

        # Validate required keys in the JSON data
        self.validate_json()

        self.symbols: dict[str, Any] = self.data['symbols']
        self.user_types: dict[str, Any] = self.data['user_types']
        self.base_types: dict[str, Any] = self.data['base_types']
        self.enums: dict[str, Any] = self.data['enums']

    def validate_json(self) -> None:
        """
        Validate that the JSON data contains all required keys.

        Raises
        ------
        SymbolsFileFormatError
            If the JSON data is missing any required keys.
        """
        required_keys = ['symbols', 'user_types', 'base_types', 'enums']
        for key in required_keys:
            if key not in self.data:
                raise SymbolsFileFormatError(f'JSON file is missing required key: {key}')

    def get_type(self, name: str) -> Union[dict[str, Any], None]:
        """
        Get a type definition by name.

        Parameters
        ----------
        name : str
            The name of the type to retrieve.

        Returns
        -------
        dict[str, Any] or None
            The type definition if found; otherwise, None.
        """
        if name in self.user_types:
            return self.user_types[name]
        elif name in self.base_types:
            return self.base_types[name]
        return None

    def get_os_type(self) -> OSType:
        """
        Get the operating system type based on the metadata in the ISF file.

        Returns
        -------
        OSType
            The operating system type detected from the ISF metadata.

        Raises
        ------
        SymbolsFileFormatError
            If the operating system type cannot be determined from the metadata.
        """
        metadata = self.data.get('metadata', {})
        if metadata.get('mac', False):
            return OSType.MACOS
        elif metadata.get('linux', False):
            return OSType.LINUX
        else:
            return OSType.WINDOWS

    def get_symbol(self, name: str) -> Any:
        """
        Get a symbol definition by name.

        Parameters
        ----------
        name : str
            The name of the symbol to retrieve.

        Returns
        -------
        Any
            The symbol definition if found; otherwise, None.
        """
        return self.symbols.get(name)

    def get_enum(self, name: str) -> Any:
        """
        Get an enum definition by name.

        Parameters
        ----------
        name : str
            The name of the enum to retrieve.

        Returns
        -------
        Any
            The enum definition if found; otherwise, None.
        """
        return self.enums.get(name)
