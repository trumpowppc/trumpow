Arch Linux build guide
----------------------

**Last tested with:** 1.1.1-dev
**Test date:** 2025/08/13

This example lists the steps necessary to setup and build a command line only
trumpowd on archlinux:

```sh
pacman -S git base-devel boost libevent python db
git clone https://github.com/trumpowppc/trumpow.git
cd trumpow/
./autogen.sh
./configure --without-gui --without-miniupnpc
make
```
