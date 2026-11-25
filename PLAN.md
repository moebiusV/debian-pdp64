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
3. **A compiler and a C library.** Debian builds with GCC 14.2, binutils 2.43 and glibc 2.40. The pdp64 back end is LLVM, so a decision is needed: a GCC back end, or building Debian's packages with clang. The C library is glibc in Debian; it needs its own port (dynamic loader, TLS, relocations, syscall stubs), which depends on the dynamic-linking ABI being fixed.
4. **Debian's own infrastructure for a new architecture.** A new `dpkg` architecture name with its table entries (dpkg 1.22.22), the new triple known to `config.sub` and `config.guess` (the copies packages take from `autotools-dev` 20240727.1 and `autoconf`), and `debootstrap` (1.0.141) with its foreign and second stage for the bootstrap. Debian also has the infrastructure for unofficial ports (its ports archive keyring is in trixie). These are from knowledge of Debian and still to be verified one by one.
5. **The bootstrap build.** The 72 source packages cannot be built alone: their build dependencies (compilers, `make`, the autotools, and so on) come first. That closure is not measured yet. The cross-bootstrap tool Debian developers use for new architectures, `rebootstrap`, is not in the archive; it lives on Salsa (see the documentation below). Debian's own figure is about 500 source packages to bootstrap a new architecture, of which `rebootstrap` exercises around 100, so the build-dependency closure of our 72 is expected to be a few hundred.

## Order of work, once OpenBSD is running

1. Measure the build-dependency closure of the 72 source packages.
2. Survey Linux 6.12 for what a new architecture needs; decide how much of it the LLVM back end must be able to compile.
3. Decide the compiler (GCC back end or clang) and confirm the C library.
4. Add the architecture to `dpkg`, `config.sub` and the packages that carry their own tables.
5. Cross-bootstrap the 72 packages and their build dependencies.
6. Boot the kernel in QEMU to a shell, then run the second stage and ssh in.

## What depends on the kernel, and what does not

The bootstrap does not wait for a bootable kernel, but it does wait for the kernel's interface to userspace:

- **Needed first: the Linux ABI for the pdp64.** glibc is built against the kernel's userspace headers (`arch/pdp64` `uapi`: system-call numbers and convention, register and signal-frame layouts, `stat` and the other structures). So a minimal `arch/pdp64` skeleton with those headers comes before glibc, and fixing them depends on the architecture decisions shared with the OpenBSD plan.
- **Not needed yet: a running kernel.** Cross-building the 72 source packages and their build dependencies happens on the host.
- **Needed when something must run on the pdp64:** debootstrap's second stage, test suites, native builds, and the final boot and ssh. There are two ways to get there: boot the Linux port in QEMU, or add the pdp64 to QEMU's `linux-user` mode (which translates the system calls and runs the binaries on the host without a kernel; our QEMU is built with user mode off today). The second needs much less than a kernel and lets the bootstrap run ahead of it. *(From knowledge of how these pieces fit; not yet checked against Debian's documentation.)*

## Open

- init system: `systemd` (the default, no smaller alternative) unless that proves a problem to port;
- whether a root file system on the virtio disk needs an initramfs (probably not);
- network configuration in the minimal system: a static address or a DHCP client;
- GCC back end or clang, and glibc or another C library.

## Where the documentation is

What Debian has written on bringing up a new architecture (found by search, pages not yet read in full; some are several years old, so commands and mirror names may be out of date):

- [DebianBootstrap](https://wiki.debian.org/DebianBootstrap) and its [TODO](https://wiki.debian.org/DebianBootstrap/TODO): the bootstrap problem, the dependency cycles, and the idea of dropping architecture-independent build dependencies while bootstrapping.
- [rebootstrap](https://wiki.debian.org/HelmutGrohne/rebootstrap) (source on Salsa, `helmutg/rebootstrap`): Helmut Grohne's cross-bootstrap script, run weekly against about 20 architectures; the [debian-cross mailing list](https://lists.debian.org/debian-cross/) and `#debian-bootstrap` on OFTC are where it is discussed.
- [MultiarchCrossToolchainBootstrap](https://wiki.debian.org/MultiarchCrossToolchainBootstrap) and [MultiarchCrossToolchainBuild](https://wiki.debian.org/MultiarchCrossToolchainBuild): the staged gcc, libc and binutils build for an architecture that is not in the archive yet, with build profiles.
- [CrossBuildPackagingGuidelines](https://wiki.debian.org/CrossBuildPackagingGuidelines) and the [cross-buildable base](https://wiki.debian.org/ReleaseGoals/CrossBuildableBase) release goal.
- [Bootstrapping Debian-based distributions for new architectures](https://archive.fosdem.org/2013/schedule/event/debian_bootstrap/) (FOSDEM 2013) and the [2014 bootstrap sprint results](https://wiki.debian.org/Sprints/2014/BootstrapSprint/Results).
- [Debootstrap](https://wiki.debian.org/Debootstrap) and [EmDebian/CrossDebootstrap](https://wiki.debian.org/EmDebian/CrossDebootstrap): making the root file system from a host.
- Language compilers needed along the way: [BootstrappingGHC](https://wiki.debian.org/PortsDocs/BootstrappingGHC) and [BootstrappingFPC](https://wiki.debian.org/PortsDocs/BootstrappingFPC).
- A search for a single "porting guide" page (`PortsDocs/NewArch`) found none: the knowledge is spread over these pages and the mailing lists.
