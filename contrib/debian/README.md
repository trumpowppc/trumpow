
Debian
====================
This directory contains files used to package trumpowd/trumpow-qt
for Debian-based Linux systems. If you compile trumpowd/trumpow-qt yourself, there are some useful files here.

## trumpow: URI support ##


trumpow-qt.desktop  (Gnome / Open Desktop)
To install:

	sudo desktop-file-install trumpow-qt.desktop
	sudo update-desktop-database

If you build yourself, you will either need to modify the paths in
the .desktop file or copy or symlink your trumpow-qt binary to `/usr/bin`
and the `../../share/pixmaps/trumpow128.png` to `/usr/share/pixmaps`

trumpow-qt.protocol (KDE)

