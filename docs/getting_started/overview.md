# Overview

`Heimdall` is a Virtual Machine (VM) introspection tool built on top of [`libvmi`](https://github.com/libvmi/libvmi)
that
simplifies memory inspection and manipulation with OS-level abstractions.

Named after the all-seeing Norse guardian,`Heimdall` offers deep visibility into VM memory through its interactive
Python shell, allowing users to directly access
and modify kernel structures. This includes retrieving process lists, modifying attributes like PID or process name, and
interacting with other kernel data structures. `Heimdall` also supports accessing a process's execution context,
providing
powerful insights and control over VM internals.

This project is highly inspired by:

- [Hilda](https://github.com/doronz88/hilda.git) A powerful wrapper over the LLDB debugger for advanced debugging and
  binary analysis.
- [Volatility](https://github.com/volatilityfoundation/volatility): A memory forensics framework for analyzing volatile
  memory.
- [DRAKVUF](https://github.com/tklengyel/drakvuf): A virtualization-based agentless monitoring system for malware
  analysis.
- [rpc-project](https://github.com/doronz88/rpc-project.git) Minimalistic server (written in C) and a python3 client to
  allow calling native functions on a remote host for automation purposes