#!/usr/bin/env python3
# Copyright (c) 2014 Wladimir J. van der Laan
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
'''
A script to check that release executables only contain certain symbols
and are only linked against allowed libraries.

Example usage:

    find ../path/to/binaries -type f -executable | xargs python3 contrib/devtools/symbol-check.py
'''
import sys
from typing import List, Dict

import lief #type:ignore

# MAX_VERSIONS defines the maximum versions for dynamic symbols defined in linux
# binaries for release. These are static for each major version of Dogecoin Core.
#
# Debian 6.0.9 (Squeeze) has:
#
# - g++ version 4.4.5 (https://packages.debian.org/search?suite=default&section=all&arch=any&searchon=names&keywords=g%2B%2B)
# - libc version 2.11.3 (https://packages.debian.org/search?suite=default&section=all&arch=any&searchon=names&keywords=libc6)
# - libstdc++ version 4.4.5 (https://packages.debian.org/search?suite=default&section=all&arch=any&searchon=names&keywords=libstdc%2B%2B6)
#
# Ubuntu 10.04.4 (Lucid Lynx) has:
#
# - g++ version 4.4.3 (http://packages.ubuntu.com/search?keywords=g%2B%2B&searchon=names&suite=lucid&section=all)
# - libc version 2.11.1 (http://packages.ubuntu.com/search?keywords=libc6&searchon=names&suite=lucid&section=all)
# - libstdc++ version 4.4.3 (http://packages.ubuntu.com/search?suite=lucid&section=all&arch=any&keywords=libstdc%2B%2B&searchon=names)
#
# Taking the minimum of these as our target.
#
# According to GNU ABI document (http://gcc.gnu.org/onlinedocs/libstdc++/manual/abi.html) this corresponds to:
#   GCC 4.4.0: GCC_4.4.0
#   GCC 4.4.2: GLIBCXX_3.4.13, CXXABI_1.3.3
#   (glibc)    GLIBC_2_11

MAX_VERSIONS = {
'GCC':       (4,4,0),
'GLIBC': {
    lief.ELF.ARCH.x86_64: (2,11),
    lief.ELF.ARCH.i386:   (2,11),
    lief.ELF.ARCH.ARM:    (2,11),
    lief.ELF.ARCH.AARCH64:(2,17),
    lief.ELF.ARCH.PPC64:  (2,17),
    lief.ELF.ARCH.RISCV:  (2,27),
},
'CXXABI':  (1,3,3),
'GLIBCXX': (3,4,13),
'V':         (0,5,0),  # xkb (trumpow-qt only)
}

# Ignore symbols that are exported as part of every executable
IGNORE_EXPORTS = {
  '_edata', '_end', '_init', '__bss_start', '_fini', '_IO_stdin_used',
  'stdin', 'stdout', 'stderr'
}

# Expected linker-loader names can be found here:
# https://sourceware.org/glibc/wiki/ABIList?action=recall&rev=16
ELF_INTERPRETER_NAMES: Dict[lief.ELF.ARCH, Dict[lief.ENDIANNESS, str]] = {
    lief.ELF.ARCH.i386: {
        lief.ENDIANNESS.LITTLE: "/lib/ld-linux.so.2",
    },
    lief.ELF.ARCH.x86_64:  {
        lief.ENDIANNESS.LITTLE: "/lib64/ld-linux-x86-64.so.2",
    },
    lief.ELF.ARCH.ARM:     {
        lief.ENDIANNESS.LITTLE: "/lib/ld-linux-armhf.so.3",
    },
    lief.ELF.ARCH.AARCH64: {
        lief.ENDIANNESS.LITTLE: "/lib/ld-linux-aarch64.so.1",
    },
    lief.ELF.ARCH.PPC64:   {
        lief.ENDIANNESS.BIG: "/lib64/ld64.so.1",
        lief.ENDIANNESS.LITTLE: "/lib64/ld64.so.2",
    },
    lief.ELF.ARCH.RISCV:    {
        lief.ENDIANNESS.LITTLE: "/lib/ld-linux-riscv64-lp64d.so.1",
    },
}

# Allowed NEEDED libraries
ELF_ALLOWED_LIBRARIES = {
# trumpowd and trumpow-qt
'libgcc_s.so.1', # GCC base support
'libc.so.6', # C library
'libpthread.so.0', # threading
'libanl.so.1', # DNS resolve
'libm.so.6', # math library
'librt.so.1', # real-time (clock)
'ld-linux-x86-64.so.2', # 64-bit dynamic linker
'ld-linux.so.2', # 32-bit dynamic linker
'ld-linux-aarch64.so.1', # 64-bit ARM dynamic linker
'ld-linux-armhf.so.3', # 32-bit ARM dynamic linker
# trumpow-qt only
'libxcb.so.1', # part of X11
'libxkbcommon.so.0', # keyboard keymapping
'libxkbcommon-x11.so.0', # keyboard keymapping
'libfontconfig.so.1', # font support
'libfreetype.so.6', # font parsing
'libdl.so.2' # programming interface to dynamic linker
}

MACHO_ALLOWED_LIBRARIES = {
# bitcoind and bitcoin-qt
'libc++.1.dylib', # C++ Standard Library
'libSystem.B.dylib', # libc, libm, libpthread, libinfo
# bitcoin-qt only
'AppKit', # user interface
'ApplicationServices', # common application tasks.
'Carbon', # deprecated c back-compat API
'ColorSync',
'CoreFoundation', # low level func, data types
'CoreGraphics', # 2D rendering
'CoreServices', # operating system services
'CoreText', # interface for laying out text and handling fonts.
'CoreVideo', # video processing
'Foundation', # base layer functionality for apps/frameworks
'ImageIO', # read and write image file formats.
'IOKit', # user-space access to hardware devices and drivers.
'IOSurface', # cross process image/drawing buffers
'libobjc.A.dylib', # Objective-C runtime library
'Metal', # 3D graphics
'Security', # access control and authentication
'QuartzCore', # animation
}

PE_ALLOWED_LIBRARIES = {
'ADVAPI32.dll', # security & registry
'CRYPT32.dll', # crypto functions
'IPHLPAPI.DLL', # IP helper API
'KERNEL32.dll', # win32 base APIs
'msvcrt.dll', # C standard library for MSVC
'SHELL32.dll', # shell API
'USER32.dll', # user interface
'WS2_32.dll', # sockets
# bitcoin-qt only
'COMDLG32.DLL', # common dialogs like "open file"
'comdlg32.dll', # same as above but lowercase in win64 binary
'dwmapi.dll', # desktop window manager
'GDI32.dll', # graphics device interface
'IMM32.DLL', # input method editor
'IMM32.dll', # same as above but lowercase extension in win64 binary
'NETAPI32.dll',
'ole32.dll', # component object model
'OLEAUT32.dll', # OLE Automation API
'SHLWAPI.dll', # light weight shell API
'USERENV.dll',
'UxTheme.dll',
'VERSION.dll', # version checking
'WINMM.DLL', # WinMM audio API
'WINMM.dll', # same as above but lowercase extension in win64 binary
'WINSPOOL.DRV', # Printer spooler driver for paper wallet printing
'WTSAPI32.dll',
}

def check_version(max_versions, version, arch) -> bool:
    (lib, _, ver) = version.rpartition('_')
    ver = tuple([int(x) for x in ver.split('.')])
    if not lib in max_versions:
        return False
    if isinstance(max_versions[lib], tuple):
        return ver <= max_versions[lib]
    else:
        return ver <= max_versions[lib][arch]

def check_imported_symbols(binary) -> bool:
    ok: bool = True

    for symbol in binary.imported_symbols:
        if not symbol.imported:
            continue

        version = symbol.symbol_version if symbol.has_version else None

        if version:
            aux_version = version.symbol_version_auxiliary.name if version.has_auxiliary_version else None
            if aux_version and not check_version(MAX_VERSIONS, aux_version, binary.header.machine_type):
                print(f'{filename}: symbol {symbol.name} from unsupported version {version}')
                ok = False
    return ok

def check_exported_symbols(binary) -> bool:
    ok: bool = True

    for symbol in binary.dynamic_symbols:
        if not symbol.exported:
            continue
        name = symbol.name
        if binary.header.machine_type == lief.ELF.ARCH.RISCV or name in IGNORE_EXPORTS:
            continue
        print(f'{binary.name}: export of symbol {name} not allowed!')
        ok = False
    return ok

def check_ELF_libraries(binary) -> bool:
    ok: bool = True
    for library in binary.libraries:
        if library not in ELF_ALLOWED_LIBRARIES:
            print(f'{filename}: {library} is not in ALLOWED_LIBRARIES!')
            ok = False
    return ok

def check_MACHO_libraries(binary) -> bool:
    ok: bool = True
    for dylib in binary.libraries:
        split = dylib.name.split('/')
        if split[-1] not in MACHO_ALLOWED_LIBRARIES:
            print(f'{split[-1]} is not in ALLOWED_LIBRARIES!')
            ok = False
    return ok

def check_MACHO_min_os(binary) -> bool:
    if binary.build_version.minos == [10,15,0]:
        return True
    return False

def check_MACHO_sdk(binary) -> bool:
    if binary.build_version.sdk == [11, 0, 0]:
        return True
    return False

def check_PE_libraries(binary) -> bool:
    ok: bool = True
    for dylib in binary.libraries:
        if dylib not in PE_ALLOWED_LIBRARIES:
            print(f'{dylib} is not in ALLOWED_LIBRARIES!')
            ok = False
    return ok

def check_PE_subsystem_version(binary) -> bool:
    major: int = binary.optional_header.major_subsystem_version
    minor: int = binary.optional_header.minor_subsystem_version
    if major == 6 and minor == 1:
        return True
    return False

def check_ELF_interpreter(binary) -> bool:
    expected_interpreter = ELF_INTERPRETER_NAMES[binary.header.machine_type][binary.abstract.header.endianness]

    return binary.concrete.interpreter == expected_interpreter

CHECKS = {
lief.EXE_FORMATS.ELF: [
    ('IMPORTED_SYMBOLS', check_imported_symbols),
    ('EXPORTED_SYMBOLS', check_exported_symbols),
    ('LIBRARY_DEPENDENCIES', check_ELF_libraries),
    ('INTERPRETER_NAME', check_ELF_interpreter),
],
lief.EXE_FORMATS.MACHO: [
    ('DYNAMIC_LIBRARIES', check_MACHO_libraries),
    ('MIN_OS', check_MACHO_min_os),
    ('SDK', check_MACHO_sdk),
],
lief.EXE_FORMATS.PE: [
    ('DYNAMIC_LIBRARIES', check_PE_libraries),
    #('SUBSYSTEM_VERSION', check_PE_subsystem_version),
    #Note: needs to be set during build before we can check for it
]
}

if __name__ == '__main__':
    retval: int = 0
    for filename in sys.argv[1:]:
        try:
            binary = lief.parse(filename)
            etype = binary.format
            if etype == lief.EXE_FORMATS.UNKNOWN:
                print(f'{filename}: unknown executable format')
                retval = 1
                continue

            failed: List[str] = []
            for (name, func) in CHECKS[etype]:
                if not func(binary):
                    failed.append(name)
            if failed:
                print(f'{filename}: failed {" ".join(failed)}')
                retval = 1
        except IOError:
            print(f'{filename}: cannot open')
            retval = 1
    sys.exit(retval)
