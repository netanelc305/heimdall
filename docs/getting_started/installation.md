# Installation

This guide assumes that you already have a Xen or KVM-VMI setup. If not, please refer to the following resources to set
up your environment:

- [Setting up Xen](https://github.com/xen-project/xen)
- [Setting up KVM-VMI](https://github.com/KVM-VMI/kvm-vmi)

`Heimdall` requires the `libvmi` library for Virtual Machine Introspection capabilities. Follow the instructions in the
`libvmi` repository to build and install it:

## 1. Install [`libvmi`](https://github.com/libvmi/libvmi)

```shell
sudo apt install git build-essential gcc libtool cmake pkg-config check libglib2.0-dev libvirt-dev flex bison libjson-c-dev
git clone https://github.com/libvmi/libvmi
cd libvmi
autoreconf -vif
```

Xen

```shell
./configure --disable-kvm --disable-bareflank --disable-file
make
sudo make install
```

KVM

```shell
./configure --disable-xen --disable-bareflank --disable-file
make
sudo make install
```

## 2. Install  [`libvmi-python`](https://github.com/libvmi/python)

```shell
git clone https://github.com/libvmi/python libvmi-python
cd libvmi-python
python3 setup.py build
python3 setup.py install
```

## 3. Install `Heimdall`

Finally, install `Heimdall` itself:

```shell
python3 -m pip install heimdall-vmi
```

> **Note**: If you prefer not to use `sudo` when running `Heimdall`, I recommend installing it with `pipx`. After
> installing with `pipx`, add `setuid` permissions to the virtual environment, allowing `Heimdall` to run with elevated
> privileges without requiring `sudo` each time.

To install `Heimdall` using `pipx`:

```shell
pipx install heimdall-vmi
```

Then, set `setuid` permissions on the virtual environment’s binaries:

```shell
sudo chmod u+s $(which heimdall-vmi)
```

This will allow `Heimdall` to execute with necessary permissions directly from the `pipx` virtual environment.