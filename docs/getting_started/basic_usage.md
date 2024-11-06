# Basic Usage

## Step 1: Generate an ISF File

To properly parse kernel structures, you first need an **Intermediate Symbol File (ISF)**, which provides a structured
view of kernel symbols and types. `Heimdall` simplifies this process with a CLI command, eliminating the need to
manually generate the ISF file (Currently not supports windows).

To create an ISF for your VM, run:

```shell
sudo heimdall isf create VM_NAME
```

**Note**: For more details on the ISF format, see
the [Volatility documentation](https://volatility3.readthedocs.io/en/latest/symbol-tables.html).

## Step 2: Connect to the VM

After creating the OS profile, you can connect to the target VM using the command:

```shell
sudo heimdall connect VM_NAME
```

OR

```shell
sudo heimdall connect VM_NAME -j windows.json -k /path/to/kvmi
```

You’ll see output indicating that `Heimdall` has successfully initialized:

```shell
Initializing SymbolsJar: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 75671/75671 [00:00<00:00, 154738.17it/s]

Heimdall has been successfully loaded! 😎
Usage:
 h   Global to access heimdall features.
 k   Global to access kernel context.

Have a nice flight ✈️! Starting an IPython shell...

IPython profile: heimdall

Heimdall:> 
```

## Interacting with Heimdall Features via `h`

The global variable `h` is your primary interface to `Heimdall`'s high-level features. It is derived from the `heimdall`
core and provides a convenient way to access and interact with various subsystems within the virtual machine
environment.

### Current Capabilities

Currently, `h` provides access to process-related functionalities through the `processes` module. You can use it to:

- **List all processes**:

  ```shell
  Heimdall:> h.processes.list()
  Heimdall:> 
  [<WindowsProcess PID:4 PATH:System>,
   <WindowsProcess PID:108 PATH:Registry>,
   <WindowsProcess PID:352 PATH:\Windows\System32\smss.exe>,
   <WindowsProcess PID:448 PATH:\Windows\System32\csrss.exe>,
    ...
   <WindowsProcess PID:7692 PATH:\Windows\System32\RuntimeBroker.exe>,
   <WindowsProcess PID:0 PATH:>]
  ```

- **Get a process by PID**:

  ```shell
  Heimdall:> h.processes.get_by_pid(460)
  Heimdall:> <WindowsProcess PID:460 PATH:userinit.exe>
  ```

- **Get a process by name**:

  ```shell
  Heimdall:> h.processes.get_by_name('smss.exe')
  Heimdall:> <WindowsProcess PID:352 PATH:\Windows\System32\smss.exe>
  ```

- **Interact with a process's memory**:

  ```shell

  Heimdall:> smss = h.processes.get_by_name('smss.exe')
  Heimdall:> smss.peek(0x7ff7b66c1000,4)
  Heimdall:> b'\xcc\xcc\xcc\xcc'
  
  Heimdall:> smss.disass(0x7ff7b66c1000,10)                   # Reads 4 bytes from smss's VM space.
  Heimdall:> 
  [<CsInsn 0x7ff7b66c1000 [cc]: int3 >,                       # Disassemble 
   <CsInsn 0x7ff7b66c1001 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1002 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1003 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1004 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1005 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1006 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1007 [cc]: int3 >,
   <CsInsn 0x7ff7b66c1008 [b001]: mov al, 1>]

  Heimdall:> smss.poke(0x7ff7b66c1000,b'AAAA')                # Writes 4 bytes from smss's VM space.
  Heimdall:> smss.peek(0x7ff7b66c1000,4)
  Heimdall:> b'AAAA'
  ```
