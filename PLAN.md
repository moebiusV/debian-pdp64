# Debian 13 on the pdp64: the plan

A port of Debian 13 ("trixie", point release 13.8 at the time of writing) to the pdp64: the smallest bootable Debian system you can ssh into.

**Status:** setup and first measurements only. Work on this port starts after the [OpenBSD port](https://moebiusv.github.io/openbsd-pdp64/PLAN) is running, because most of what Debian needs from the machine, the compiler and the emulator is what OpenBSD needs first.

## The target system

A system that boots to a login and accepts an ssh connection, and nothing more. Measured from the signed archive indexes ([the minimal system](docs/minimal-system.md)):

- about **116 binary packages**, 157 MB installed, for the 22 Essential packages plus `apt`, `openssh-server`, `iproute2` and an init system;
- of these **100 are architecture-dependent** and must be built for the pdp64; they come from only **72 source packages**; the other 16 are architecture-independent and need no port;
- choosing `sysvinit` instead of `systemd` saves nothing (120 packages against 116), so the default init stays;
- the kernel is not in that count: it is the pdp64 Linux port.

## What must be ready before it can boot

1. **What OpenBSD needs first, shared.** The architecture decisions (system-call convention, atomics, TLS, the dynamic-linking ABI, the register and stack rules, interrupt delivery, timer, entropy) and the emulator work (virtio disk, network and entropy on PCI Express, more RAM, the kernel and user page-table split) are the same items as in the OpenBSD plan. Debian adds no machine requirement of its own that OpenBSD does not already have.
2. **A Linux kernel for the pdp64** (`arch/pdp64`). Debian 13 ships the 6.12 series (source package `linux`, 6.12.8 at release, security updates since), so the port is made against 6.12. This is a separate, large piece of work: it shares only the architecture decisions with the OpenBSD kernel. A survey of what Linux needs per architecture (the way the OpenBSD assembly was inventoried) is the first thing to do for it; the pdp64 repository's kernel assembly survey already counted Linux's.
3. **A GNU toolchain and a C library: a GCC back end (decided).** Debian builds with GCC 14.2, binutils 2.43 and glibc 2.40, and Debian's dpkg team requires support merged upstream in at least binutils, GCC and the C library before it adds an architecture name ([the dpkg FAQ](https://wiki.debian.org/Teams/Dpkg/FAQ)); we found no Debian port bootstrapped without GCC ([the porting resources](docs/porting-resources.md)). So the pdp64 gets a GCC back end and a binutils port (assembler, linker, the tools), in addition to the LLVM back end that OpenBSD uses; the kernel must also build with whichever compiler we use. glibc needs its own port (dynamic loader, TLS, relocations, syscall stubs), which depends on the dynamic-linking ABI being fixed.
4. **Debian's own infrastructure for a new architecture.** A new `dpkg` architecture name with its table entries (dpkg 1.22.22), the new triple known to `config.sub` and `config.guess` (the copies packages take from `autotools-dev` 20240727.1 and `autoconf`), and `debootstrap` (1.0.141) with its foreign and second stage for the bootstrap. Debian also has the infrastructure for unofficial ports (its ports archive keyring is in trixie). These are from knowledge of Debian and still to be verified one by one.
5. **The bootstrap build.** The 72 source packages cannot be built alone: their build dependencies (compilers, `make`, the autotools, and so on) come first. That closure is not measured yet. The cross-bootstrap tool Debian developers use for new architectures, `rebootstrap`, is not in the archive; it lives on Salsa (see the documentation below). Debian's own figure is about 500 source packages to bootstrap a new architecture, of which `rebootstrap` exercises around 100, so the build-dependency closure of our 72 is expected to be a few hundred.

## Order of work, once OpenBSD is running

1. Measure the build-dependency closure of the 72 source packages.
2. Survey Linux 6.12 for what a new architecture needs; decide how much of it the LLVM back end must be able to compile.
3. Start the GNU side: the triplet in GNU config, binutils, then the GCC back end, with glibc after them.
4. Add the architecture to `dpkg`, `config.sub` and the packages that carry their own tables.
5. Cross-bootstrap the 72 packages and their build dependencies.
6. Boot the kernel in QEMU to a shell, then run the second stage and ssh in.

## What depends on the kernel, and what does not

The bootstrap does not wait for a bootable kernel, but it does wait for the kernel's interface to userspace:

- **Needed first: the Linux ABI for the pdp64.** glibc is built against the kernel's userspace headers (`arch/pdp64` `uapi`: system-call numbers and convention, register and signal-frame layouts, `stat` and the other structures). So a minimal `arch/pdp64` skeleton with those headers comes before glibc, and fixing them depends on the architecture decisions shared with the OpenBSD plan.
- **Not needed yet: a running kernel.** Cross-building the 72 source packages and their build dependencies happens on the host.
- **Needed when something must run on the pdp64:** debootstrap's second stage, test suites, native builds, and the final boot and ssh. The port is not finished until the Linux kernel boots in QEMU and runs the whole system: that is the full deliverable and is not optional. QEMU's `linux-user` mode ([qemu-pdp64](https://moebiusv.github.io/qemu-pdp64/) gets it, alongside the full system emulation) is an additional tool on the way: it translates the system calls and runs the binaries on the host without a kernel, so the bootstrap and the test suites can run ahead of the kernel port. It must never become the only way anything runs. *(From knowledge of how these pieces fit; not yet checked against Debian's documentation.)*

## Open

- init system: `systemd` (the default, no smaller alternative) unless that proves a problem to port;
- whether a root file system on the virtio disk needs an initramfs (probably not);
- network configuration in the minimal system: a static address or a DHCP client;
- the C library is glibc, Debian's own; nothing else is being considered.

## Where the documentation is

[Porting resources](docs/porting-resources.md) collects what Debian and others have written on bringing up a new architecture: Debian's own guide and policies, the dpkg and ports requirements, `rebootstrap`, the riscv64 and loong64 case studies, and the kernel, glibc and toolchain pieces, with what we could not find. There is no step-by-step Debian porting recipe; the page says where the knowledge is.
