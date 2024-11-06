import logging
from typing import Union

from tqdm import tqdm

from heimdall.core.descriptors import ArrayKind, BaseKind, BitFieldKind, ClassKind, ComplexKind, EnumKind, Field, \
    FunctionKind, KindDescriptor, PointerKind, StructKind, SymbolDescriptor, UnionKind, UnresolvedKind
from heimdall.core.isf_file import ISFFile

logger = logging.getLogger(__name__)
TYPE_MAPPING = {
    'int': ('i', 4),
    'str': ('str', None),
    'arr': ('B', None),
    'short': ('h', 2),
    'char': ('c', 1),
    'double': ('d', 8),
    'float': ('f', 4),
    'long': ('q', 8),
    'longlong_unsigned': ('Q', 8),
    'unsigned_int': ('I', 4),
    'unsigned_short': ('H', 2),
    'unsigned_char': ('B', 1),
    'unsigned_int128': ('QQ', 16),
    'pointer': ('Q', 8),
    '__ARRAY_SIZE_TYPE__': ('Q', 8),
    'bool': ('?', 1),
    '_Bool': ('?', 1),
    'signed char': ('b', 1),
    'long int': ('q', 8),
    'long long int': ('q', 8),
    'long long': ('q', 8),
    'unsigned long long': ('Q', 8),
    'long long unsigned int': ('Q', 8),
    'long unsigned int': ('Q', 8),
    'unsigned char': ('B', 1),
    'unsigned int': ('I', 4),
    'unsigned short': ('H', 2),
    'unsigned long': ('Q', 8),
    'unsigned __int128': ('QQ', 16),
    'void': ('Q', 8),  # same as pointer
    'HRESULT': ('I', 4),  # Based on 'unsigned int'
    'f32': ('f', 4),  # Same as 'float'
    'wchar': ('H', 2),  # 2-byte wchar
    '__int128': ('QQ', 16),
    '__int128 unsigned': ('QQ', 16),
    'short int': ('h', 2),
    'short unsigned int': ('H', 2),
    'ssizetype': ('q', 8),  # Assuming ssize_t to be equivalent to signed long
}


class SymbolsJar:
    """
    Represents a container for symbol and type information, responsible for resolving
    and storing symbols and types from a given context profile.

    The `SymbolsJar` class provides methods to retrieve types, symbols, and enums by name.
    It initializes base types, user-defined types, enums, and symbols from the context's profile.
    """

    def __init__(self, profile: ISFFile):
        """
        Initialize the SymbolsJar.

        Parameters
        ----------
        profile : ISFFile
            The symbols file used for populating types and symbols.
        """
        self._resolving_types = set()
        self._resolved_cache = {}
        self._profile = profile
        self.base_types = {}
        self.enums = {}
        self.user_types = {}
        self.symbols = {}

        total_steps = (
                len(self._profile.base_types) +
                len(self._profile.enums) +
                len(self._profile.user_types) +
                len(self._profile.symbols)
        )

        with tqdm(total=total_steps, desc="Initializing SymbolsJar") as pbar:
            self._resolve_base_types(pbar)
            self._resolve_enums(pbar)
            self._resolve_user_types(pbar)
            self._resolve_symbols(pbar)

    def get_type(self, name: str) -> KindDescriptor:
        """
        Get a type by its name.

        Parameters
        ----------
        name : str
            The name of the type to retrieve.

        Returns
        -------
        KindDescriptor
            The type descriptor corresponding to the given name.

        Raises
        ------
        ValueError
            If the type with the given name is not found.
        """
        if name in self.user_types:
            return self.user_types[name]
        if name in self.base_types:
            return self.base_types[name]
        raise ValueError(f"Type '{name}' not found")

    def get_symbol(self, name: str) -> SymbolDescriptor:
        """
        Get a symbol by its name.

        Parameters
        ----------
        name : str
            The name of the symbol to retrieve.

        Returns
        -------
        SymbolDescriptor
            The symbol descriptor corresponding to the given name.
        """
        return self.symbols[name]

    def get_enum(self, name: str) -> EnumKind:
        """
        Get an enum by its name.

        Parameters
        ----------
        name : str
            The name of the enum to retrieve.

        Returns
        -------
        EnumKind
            The enum descriptor corresponding to the given name, or None if not found.
        """
        return self.enums.get(name)

    def _resolve_base_types(self, pbar: tqdm) -> None:
        """
        Resolve base types from the profile.

        Parameters
        ----------
        pbar : tqdm.tqdm
            A progress bar instance to update during the resolution process.
        """
        for name, dtype in self._profile.base_types.items():
            self.base_types[name] = BaseKind(
                name, dtype['size'], fmt=TYPE_MAPPING[name][0]
            )
            pbar.update(1)

    def _resolve_user_types(self, pbar: tqdm) -> None:
        """
        Resolve user-defined types from the profile.

        Parameters
        ----------
        pbar : tqdm.tqdm
            A progress bar instance to update during the resolution process.
        """
        user_types_data = self._profile.user_types.items()
        for name, dtype in user_types_data:
            if name in self._resolved_cache:
                self.user_types[name] = self._resolved_cache[name]
            else:
                self.user_types[name] = self._resolve_complex(dtype, name)
            pbar.update(1)

    def _resolve_enums(self, pbar: tqdm) -> None:
        """
        Resolve enums from the profile.

        Parameters
        ----------
        pbar : tqdm.tqdm
            A progress bar instance to update during the resolution process.
        """
        enums_data = self._profile.enums.items()
        for name, edata in enums_data:
            fmt, size = TYPE_MAPPING[edata['base']]
            self.enums[name] = EnumKind(
                name=name, size=size, fmt=fmt, constants=edata['constants']
            )
            pbar.update(1)

    def _resolve_symbols(self, pbar: tqdm) -> None:
        """
        Resolve symbols from the profile.

        Parameters
        ----------
        pbar : tqdm.tqdm
            A progress bar instance to update during the resolution process.
        """
        symbols_data = self._profile.symbols.items()
        for name, dtype in symbols_data:
            kind = self._kind_factory(dtype['type']) if 'type' in dtype else None
            self.symbols[name] = SymbolDescriptor(name, dtype['address'], kind)
            pbar.update(1)

    def _kind_factory(self, data: dict) -> KindDescriptor:
        """
        Create a kind descriptor from the given data.

        Parameters
        ----------
        data : dict
            The data dictionary containing type information.

        Returns
        -------
        KindDescriptor
            The kind descriptor created based on the data.
        """
        kind_type = data['kind']
        kind_mapping = {
            'base': self._resolve_base,
            'pointer': self._resolve_pointer,
            'function': self._resolve_function,
            'class': self._resolve_class,
            'bitfield': self._resolve_bitfield,
            'array': self._resolve_array,
            'enum': self._resolve_enum,
            'struct': self._resolve_struct_union,
            'union': self._resolve_struct_union
        }
        return kind_mapping.get(kind_type, self._resolve_default)(data)

    def _resolve_base(self, data: dict) -> BaseKind:
        """
        Resolve a base kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing base type information.

        Returns
        -------
        BaseKind
            The resolved base kind descriptor.
        """
        return self.base_types[data['name']]

    def _resolve_pointer(self, data: dict) -> PointerKind:
        """
        Resolve a pointer kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing pointer type information.

        Returns
        -------
        PointerKind
            The resolved pointer kind descriptor.
        """
        return PointerKind(
            name=data['kind'],
            subtype=self._kind_factory(data['subtype']),
            fmt=TYPE_MAPPING[data['kind']][0],
            size=TYPE_MAPPING[data['kind']][1]
        )

    @staticmethod
    def _resolve_default(data: dict) -> UnresolvedKind:
        """
        Resolve a default (unresolved) kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing type information.

        Returns
        -------
        UnresolvedKind
            An unresolved kind descriptor.
        """
        return UnresolvedKind(name=data['kind'], data=data, size=0)

    @staticmethod
    def _resolve_function(data: dict) -> FunctionKind:
        """
        Resolve a function kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing function type information.

        Returns
        -------
        FunctionKind
            The resolved function kind descriptor.
        """
        return FunctionKind(
            name=data['kind'],
            fmt=TYPE_MAPPING['pointer'][0],
            size=TYPE_MAPPING['pointer'][1]
        )

    @staticmethod
    def _resolve_class(data: dict) -> ClassKind:
        """
        Resolve a class kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing class type information.

        Returns
        -------
        ClassKind
            The resolved class kind descriptor.
        """
        return ClassKind(
            name=data['name'],
            fmt=TYPE_MAPPING['pointer'][0],
            size=TYPE_MAPPING['pointer'][1]
        )

    def _resolve_bitfield(self, data: dict) -> BitFieldKind:
        """
        Resolve a bitfield kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing bitfield type information.

        Returns
        -------
        BitFieldKind
            The resolved bitfield kind descriptor.
        """
        base_type: BaseKind = self._kind_factory(data['type'])
        return BitFieldKind(
            name=data['kind'],
            size=base_type.size,
            bit_length=data['bit_length'],
            bit_position=data['bit_position'],
            base_type=base_type
        )

    def _resolve_array(self, data: dict) -> ArrayKind:
        """
        Resolve an array kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing array type information.

        Returns
        -------
        ArrayKind
            The resolved array kind descriptor.
        """
        st: KindDescriptor = self._kind_factory(data['subtype'])
        return ArrayKind(
            name=data['kind'],
            count=data['count'],
            subtype=st,
            size=st.size * data['count']
        )

    def _resolve_enum(self, data: dict) -> EnumKind:
        """
        Resolve an enum kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing enum type information.

        Returns
        -------
        EnumKind
            The resolved enum kind descriptor.
        """
        return self.enums[data['name']]

    def _resolve_struct_union(self, data: dict) -> Union[UnresolvedKind, ComplexKind]:
        """
        Resolve a struct or union kind.

        Parameters
        ----------
        data : dict
            The data dictionary containing struct or union type information.

        Returns
        -------
        Union[UnresolvedKind, ComplexKind]
            The resolved struct or union kind descriptor.
        """
        name = data.get('name')
        if name:
            if name in self._resolved_cache:
                return self._resolved_cache[name]
            elif name in self._resolving_types:
                return UnresolvedKind(name=data['kind'], data=data, size=0)
            else:
                self._resolving_types.add(name)
                user_type_data = self._profile.user_types.get(name)
                if not user_type_data:
                    return UnresolvedKind(name=data['kind'], data=data, size=0)
                resolved: ComplexKind = self._resolve_complex(user_type_data, name)
                self._resolved_cache[name] = resolved
                self._resolving_types.remove(name)
                return resolved
        else:
            return self._resolve_complex(data, name)

    def _resolve_complex(self, data: dict, name: str) -> ComplexKind:
        """
        Resolve a complex kind (struct or union).

        Parameters
        ----------
        data : dict
            The data dictionary containing complex type information.
        name : str
            The name of the complex type.

        Returns
        -------
        ComplexKind
            The resolved complex kind descriptor.
        """
        size = data['size']
        fields = self._process_fields(data['fields'])
        if data['kind'] == 'union':
            ret: UnionKind = UnionKind(size=size, fields=fields, name=name)
        else:
            ret: StructKind = StructKind(size=size, fields=fields, name=name)
        self._resolved_cache[name] = ret
        return ret

    def _process_fields(self, data: dict) -> dict[str, Field]:
        """
        Process and resolve fields of a complex type.

        Parameters
        ----------
        data : dict
            The data dictionary containing field information.

        Returns
        -------
        dict of str to Field
            A dictionary mapping field names to `Field` instances.
        """
        fields = {}
        for k, v in data.items():
            if v.get('anonymous'):
                anonymous_fields = self._profile.user_types[v['type']['name']]['fields']
                for v1 in anonymous_fields.values():
                    v1['offset'] += v['offset']
                fields.update(self._process_fields(anonymous_fields))
            else:
                fields[k] = Field(v['offset'], self._kind_factory(v['type']))
        return dict(sorted(fields.items(), key=lambda item: item[1].offset))
