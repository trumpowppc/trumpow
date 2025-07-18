# Trumpow Snap Packaging

Commands for building and uploading a Trumpow Core Snap to the Snap Store. Anyone on amd64 (x86_64), arm64 (aarch64), or i386 (i686) should be able to build it themselves with these instructions. This would pull the official Trumpow binaries from the releases page, verify them, and install them on a user's machine.

## Building Locally
```
sudo apt install snapd
sudo snap install --classic snapcraft
sudo snapcraft
```

### Installing Locally
```
snap install \*.snap --devmode
```

### To Upload to the Snap Store
```
snapcraft login
snapcraft register trumpow
snapcraft upload \*.snap
sudo snap install trumpow
```

### Usage
```
trumpow-unofficial.cli # for trumpow-cli
trumpow-unofficial.d # for trumpowd
trumpow-unofficial.qt # for trumpow-qt
trumpow-unofficial.test # for test_trumpow
trumpow-unofficial.tx # for trumpow-tx
```

### Uninstalling
```
sudo snap remove trumpow-unofficial
```