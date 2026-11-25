# The minimal system

What a bootable Debian 13 you can ssh into consists of, measured with `tools/closure.py` from the signed archive indexes of the release in `BASE` (trixie 13.8, main, amd64). The kernel is not counted; it is ours.

Roots: every Essential package, `apt`, `openssh-server`, `iproute2`, and an init system. Dependencies are followed the way `debootstrap` does (first alternative, a provider for a virtual package), so the count is close to `debootstrap --variant=minbase` plus ssh, not identical to it.

Essential packages: 22

| variant | binary packages | architecture-dependent | architecture-independent | source packages to build for the pdp64 |
|---|---:|---:|---:|---:|
| systemd | 116 | 100 | 16 | 72 |
| sysvinit | 120 | 102 | 18 | 74 |

Installed size of the systemd variant: 157 MB.

Source packages of the systemd variant, with the architecture-dependent binaries each makes:

- `acl`: `libacl1`
- `apparmor`: `libapparmor1`
- `apt`: `apt`, `libapt-pkg7.0`
- `attr`: `libattr1`
- `audit`: `libaudit1`
- `base-files`: `base-files`
- `base-passwd`: `base-passwd`
- `bash`: `bash`
- `bzip2`: `libbz2-1.0`
- `cdebconf`: `libdebconfclient0`
- `coreutils`: `coreutils`
- `dash`: `dash`
- `db5.3`: `libdb5.3t64`
- `debianutils`: `debianutils`
- `diffutils`: `diffutils`
- `dpkg`: `dpkg`
- `e2fsprogs`: `libcom-err2`
- `elfutils`: `libelf1t64`
- `findutils`: `findutils`
- `gawk`: `gawk`
- `gcc-14`: `gcc-14-base`, `libgcc-s1`, `libstdc++6`
- `glibc`: `libc-bin`, `libc6`
- `gmp`: `libgmp10`
- `grep`: `grep`
- `gzip`: `gzip`
- `hostname`: `hostname`
- `iproute2`: `iproute2`
- `iptables`: `libxtables12`
- `keyutils`: `libkeyutils1`
- `krb5`: `libgssapi-krb5-2`, `libk5crypto3`, `libkrb5-3`, `libkrb5support0`
- `libbpf`: `libbpf1`
- `libbsd`: `libbsd0`
- `libcap-ng`: `libcap-ng0`
- `libcap2`: `libcap2`, `libcap2-bin`
- `libcbor`: `libcbor0.10`
- `libedit`: `libedit2`
- `libfido2`: `libfido2-1`
- `libmd`: `libmd0`
- `libmnl`: `libmnl0`
- `libseccomp`: `libseccomp2`
- `libselinux`: `libselinux1`
- `libsemanage`: `libsemanage2`
- `libsepol`: `libsepol2`
- `libsigsegv`: `libsigsegv2`
- `libtext-charwidth-perl`: `libtext-charwidth-perl`
- `libtirpc`: `libtirpc3t64`
- `libxcrypt`: `libcrypt1`
- `libzstd`: `libzstd1`
- `lz4`: `liblz4-1`
- `mpfr4`: `libmpfr6`
- `ncurses`: `libncursesw6`, `libtinfo6`, `ncurses-bin`
- `nettle`: `libhogweed6t64`, `libnettle8t64`
- `openssh`: `openssh-client`, `openssh-server`, `openssh-sftp-server`
- `openssl`: `libssl3t64`, `openssl-provider-legacy`
- `pam`: `libpam-modules`, `libpam-modules-bin`, `libpam0g`
- `pcre2`: `libpcre2-8-0`
- `perl`: `perl-base`
- `procps`: `libproc2-0`, `procps`
- `readline`: `libreadline8t64`
- `rust-sequoia-sqv`: `sqv`
- `sed`: `sed`
- `shadow`: `passwd`
- `sqlite3`: `libsqlite3-0`
- `systemd`: `libsystemd-shared`, `libsystemd0`, `libudev1`, `systemd`, `systemd-sysv`
- `sysvinit`: `sysvinit-utils`
- `tar`: `tar`
- `tcp-wrappers`: `libwrap0`
- `util-linux`: `bsdutils`, `libblkid1`, `liblastlog2-2`, `libmount1`, `libsmartcols1`, `libuuid1`, `mount`, `util-linux`
- `wtmpdb`: `libwtmpdb0`
- `xxhash`: `libxxhash0`
- `xz-utils`: `liblzma5`
- `zlib`: `zlib1g`

The systemd variant has these that sysvinit has not, and the other way round:
- only systemd: systemd-sysv
- only sysvinit: initscripts, insserv, startpar, sysv-rc, sysvinit-core
