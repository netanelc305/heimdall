# Heimdall Core

## Context

The `Context` in `Heimdall` describes the virtual memory space of a process, along with a `symbols_jar` for managing
symbol information. This structure allows for easy access to memory and simplifies interactions with complex data
structures, making it possible to read and write memory directly in a user-friendly way.

## The Global `k`

One important global object, `k`, represents the **kernel context**. This provides streamlined access to kernel-related
functions, allowing for efficient exploration and manipulation of kernel memory structures.

## Symbols Jar

> **Note**: Currently, `symbols_jar` support is limited to the kernel.

The `symbols_jar` is responsible for translating the ISF (Intermediate Symbol File) into Python-like descriptor objects.
When you need to initialize a symbol with a specific type, `symbols_jar` provides the necessary type descriptors,
allowing for efficient type management and interaction with memory structures.

```shell
Heimdall:> k.symbols_jar.get_type('task_struct')
Heimdall:> <StructKind(name='task_struct', size=13696): task_struct>

Heimdall:> k.symbols_jar.get_symbol('init_task')
Heimdall:> <SymbolDescriptor: 0xffffffff8340fcc0>

Heimdall:>  k.symbols_jar.get_enum('pti_mode')
Heimdall:> <EnumKind(name='pti_mode', size=4): pti_mode>
```

## Symbols

Symbols are foundational abstractions in `Heimdall`, representing various entities within the VM's memory, such as
variables, functions, and data structures. A **symbol object** encapsulates several key components:

1. **Location**: The exact memory address of the symbol in the VM's memory.
2. **Access**: The `libvmi` instance used to access the VM's memory.
3. **Descriptor (Optional)**: Additional metadata providing context about the symbol.

These components allow for organized and structured interaction with specific memory locations.

### Creating a Symbol

Symbols can be created using two methods:

#### 1. Using `symbol` (ASLR-Aware)

The `symbol` method expects the runtime address, which includes the Address Space Layout Randomization (ASLR) offset.

```shell
Heimdall:> k.symbol(0xffffff8005d24238)
Heimdall:> <Symbol: 0xffffff8005d24238>
```

#### 2. Using `file_symbol` (Without ASLR)

The `file_symbol` method expects the symbol's address as it appears in the file (or symbol table), without considering
ASLR. `Heimdall` will then adjust the address to account for ASLR if necessary.

```shell
Heimdall:> k.file_symbol(0xffffff8005d24238)
Heimdall:> <Symbol: 0xffffff800abbc238>  # ASLR-adjusted address
```

#### Symbol with Type

A symbol can be initialized directly with a type descriptor or cast to a specific type afterward.

```shell
Heimdall:> desc = k.symbols_jar.get_type('task_struct')
Heimdall:> desc
Heimdall:> <StructKind(name='task_struct', size=13696): task_struct>

Heimdall:> k.symbol(0xffffff8005d24238, desc)
Heimdall:> <Symbol: p (task_struct*) 0xffffff8005d24238>

Heimdall:> k.symbol(0xffffff8005d24238).cast('task_struct')
Heimdall:> <Symbol: p (task_struct*) 0xffffff8005d24238>
```

In this example, we retrieve the type descriptor for `task_struct` and use it to initialize a symbol directly. Alternatively,
you can create a symbol and apply a `cast` to specify the type later. Both methods allow for type-specific access to the
symbol's memory structure.

### Direct Memory Access with `__getitem__` and `__setitem__`

`Heimdall` overrides Python’s `__getitem__` and `__setitem__` methods to facilitate direct memory access. This allows
you to perform read and write operations on the virtual machine’s memory using familiar, intuitive syntax.

#### Memory Access Methods

- **`__getitem__`**: Triggered when accessing an item at a specific index, such as `some_struct.struct_member[0]`. It
  reads the value from the specified memory address.
- **`__setitem__`**: Invoked when assigning a value to a memory location, like `some_struct.struct_member[0] = 'AAAA'`.
  This writes the new value directly to the specified memory address.

#### Example Workflow

```shell
Heimdall:> task = k.symbol(0xffff916544b40000).cast('task_struct')         # Assuming `0xffff916544b40000` is of type `task_struct`.
Heimdall:> task
Heimdall:> <Symbol(0): p (task_struct*)0xffff916544b40000>
Heimdall:> task.comm[0]                                                    # Access C-struct member as a Python attribute.
Heimdall:> 'cron'
Heimdall:> task.com[0] = 'NEWNAME'                                         # Changes the process name directly in memory.
```

To streamline your workflow, `Heimdall` provides autocomplete for struct members, simplifying navigation and interaction
with complex structures.

![Symbols Autocomplete](screen_shots/symbols_autocomplete.png)

<div style="border-left: 4px solid #FFA500; padding: 10px; background-color: #FFF3E0; margin: 10px 0;">
  <strong>⚠️ Warning</strong><br><br>
  Direct memory access can lead to VM crashes or instability. Modifying memory locations directly, such as using
  <code>p.comm[0] = 'NEWNAME'</code>, bypasses system protections and can cause unintended behavior. 
  <strong>Use direct memory access only if you are confident in what you're doing.</strong>
</div><br><br>


Since direct memory access to the kernel can lead to instability, most functionality is encapsulated within
Python objects to reduce the need for direct access. However, if raw memory access is required, the `ks` attribute
provides a direct reference to the kernel struct, enabling low-level modifications.

```shell
Heimdall:> cron = h.processes.get_by_name('cron')

Heimdall:> cron.ks
Heimdall:> <Symbol(0): p (task_struct*)0xffff916544b40000>

Heimdall:> cron.ks.comm[0]
Heimdall:> 'cron'

```

By leveraging `Context`, `k`, `symbols_jar`, and symbols, `Heimdall` offers a powerful, structured approach to
interacting with kernel memory and processes in the VM environment.