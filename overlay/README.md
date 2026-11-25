# overlay/

New files of the port, one directory per Debian source package: `overlay/<source package>/...` is
added to that package's source tree. Only files that are not in the Debian package belong here; a
change to a file the package has is a patch in `../patches/<source package>/`.
