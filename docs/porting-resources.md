# Bringing Debian up on a new CPU architecture: the documentation

Everything we could find on porting Debian to a new CPU architecture, collected in one place. Compiled on 2026-11-25 by reading the pages themselves (not just search results); the date shown with each entry is the page's own last-edit date where it has one. Entries marked **old** are more than a few years out of date, and **uncertain** means we could not read the page or could not confirm what it says. If you know of something missing, open an issue on [debian-pdp64](https://github.com/moebiusV/debian-pdp64).

## The short version

- There is **no current step-by-step "how to port Debian" recipe with commands**. The closest thing is Debian's own [PortsDocs/New](https://wiki.debian.org/PortsDocs/New), an overview of the stages. The knowledge is spread over wiki pages, mailing lists and the blog posts of people who did it.
- The path, as Debian describes it and as riscv64 and loong64 followed it: **upstream** the architecture into the GNU toolchain, the kernel and the C library; get an **architecture name into dpkg**; **cross-bootstrap** a minimal set of packages (`rebootstrap`), then build natively and import a seed into the unofficial **debian-ports** archive; automate **buildds**; finally ask to become an **official port**.
- **The gate that matters most for an LLVM-based architecture:** Debian's dpkg team requires support merged upstream in at least **binutils, GCC and the C library** before it adds an architecture. We found no Debian port bootstrapped without GCC and no documented clang-only route.

## 1. Debian's own documentation and process

| Page | What it contains | Date / status |
|---|---|---|
| [PortsDocs/New](https://wiki.debian.org/PortsDocs/New) | The best single overview: an aspirational guide through preparation, upstreaming (define the ABI and GNU triplet; merge into GNU config, binutils, GCC, GDB, kernel and libc), downstreaming (justify the port on debian-devel, get the name into dpkg), bootstrap (rebootstrap plus manual work until `build-essential` installs with `debootstrap --variant=buildd`), unofficial port (debian-ports, buildds, installer) and official port (ftp-masters, release team, DSA). Says not to skip steps. | 2026-04-23, current |
| [Teams/Dpkg/FAQ](https://wiki.debian.org/Teams/Dpkg/FAQ) ("Can we add support for new dpkg architectures?") | The requirements for a new dpkg architecture: an official GNU triplet in GNU config; support merged upstream in at least binutils, GCC and the libc; a full ABI different from every existing architecture; a bijective mapping from triplet to dpkg name; the name vetted by the porting team or the dpkg maintainers. Naming convention: append the bit width. | 2025-09-03, current |
| [DebianBootstrap](https://wiki.debian.org/DebianBootstrap) | The bootstrap concept: build profiles (`DEB_BUILD_PROFILES`) break build-dependency loops, the base system must be cross-buildable, tools such as botch analyse the build order. Links to rebootstrap, bootstrap.debian.net and bootstrappable.org. | 2026-11-14, partly **old** (much text is 2013-14) |
| [DebianBootstrap/TODO](https://wiki.debian.org/DebianBootstrap/TODO) | A maintainers' list of open problems: cross-build failures, dependency cycles (one strongly connected component of about 387 source packages) and how to break them. | 2025-08-23, **uncertain** (numbers probably stale) |
| [HelmutGrohne/rebootstrap](https://wiki.debian.org/HelmutGrohne/rebootstrap) and [source on Salsa](https://salsa.debian.org/helmutg/rebootstrap) | `rebootstrap`, the tool that tests whether an architecture can be bootstrapped from source. Patch policy (local patches are meant for upstream), per-architecture known issues, a Jenkins view, and the contact channel `#debian-bootstrap` on OFTC. The Salsa project is live (about 2,150 commits); we did not read its README, so how to drive it is not confirmed here. | wiki 2024-05-23, current |
| [bootstrap.debian.net](https://bootstrap.debian.net/) | Generated analysis files (cross-buildability, foreign install, essential set, history). Regenerated in November 2026. No prose documentation. | current |
| [PortsDocs](https://wiki.debian.org/PortsDocs) | Index of the ports sub-pages: BootstrappingFPC, GHC, OpenJDK and Rust (the self-hosted language compilers that block package sets), BuilddSetup, BuilddPorterboxSetup, CreateDebianInstallerImages, New, WhatIsUnreleased. | 2016-07-25, index **old** |
| [PortsDocs/BuilddSetup](https://wiki.debian.org/PortsDocs/BuilddSetup) | Setting up debian-ports buildds and porterboxes: patching the setup scripts for a new architecture, the `dsa-puppet` repository, key rotation. | 2023-01-27 |
| [PortsDocs/WhatIsUnreleased](https://wiki.debian.org/PortsDocs/WhatIsUnreleased) | The debian-ports `unreleased` suite: packages needing source changes go there. Versioning: `+arch` for substantial porting changes, `~arch` for bootstrap and cycle-breaking patches. Cross-built packages are generally not acceptable. | 2023-08-15 |
| [PortsDocs/CreateDebianInstallerImages](https://wiki.debian.org/PortsDocs/CreateDebianInstallerImages) | Building installer images for a port with debian-cd and a local mirror (about 60 GB). | 2025-06-09 |
| [DebianPorts](https://wiki.debian.org/DebianPorts) and [PortTemplate](https://wiki.debian.org/PortTemplate) | How to propose a new port page, and the checklist every port page fills in (triplet, dpkg status, toolchain status, rebootstrap status, `build-essential` installability, buildd, qualification). A ready-made to-do list. | 2025-06-03 / 2023-09-08 |
| [Debian ports](https://www.debian.org/ports/) | The ports that are official for the next release (amd64, arm64, armhf, i386, loong64, ppc64el, riscv64, s390x), the active unofficial ones and the dead ones. | current |
| [Debian Ports infrastructure](https://www.ports.debian.org/) | The unofficial archive (mini-dak since 2016), signed with a yearly key. A new architecture is accepted once "a minimal set of .deb packages has been ported, for example enough to run a buildd". No step-by-step instructions. | current |
| [ftp-master archive criteria](https://ftp-master.debian.org/archive-criteria.html) | The rules for becoming an official architecture: built from plain Debian sources with no external patches; a minimal imported set signed by a lead porter who is a Debian Developer; two DSA-maintainable machines (a buildd and a porter box); twelve questions covering hardware, three or more maintainers, users, kernel and toolchain support, ABI stability and an install how-to. | current |
| [ArchiveQualification](https://wiki.debian.org/ArchiveQualification) | Index of per-port qualification pages, with worked examples to copy: [riscv64](https://wiki.debian.org/ArchiveQualification/riscv64) (2024-01-30) and [loong64](https://wiki.debian.org/ArchiveQualification/loong64) (2026-04-14). | 2022-12-10 |

### dpkg and the autotools files

| Page | What it contains | Date / status |
|---|---|---|
| dpkg data tables: [cputable](https://salsa.debian.org/dpkg-team/dpkg/-/raw/main/data/cputable), [tupletable](https://salsa.debian.org/dpkg-team/dpkg/-/raw/main/data/tupletable), [abitable](https://salsa.debian.org/dpkg-team/dpkg/-/raw/main/data/abitable) | The actual files to edit. `cputable` columns: Debian CPU name, GNU CPU name, `config.guess` regex, pointer bits, endianness (for example `riscv64 riscv64 riscv64 64 little`). A plain `base-gnu-linux-<cpu>` line in `tupletable` covers a new Linux CPU. `abitable` holds ABI overrides and currently has only two. | main branch, current |
| [dpkg-architecture(1)](https://manpages.debian.org/testing/dpkg-dev/dpkg-architecture.1.en.html) | Defines architecture names, tuples, wildcards and the four tables (all must be present; `DPKG_DATADIR` overrides the path). Does not explain how to add an architecture. | dpkg 1.23.11, current |
| debian-dpkg thread on loong64: [request](https://lists.debian.org/debian-dpkg/2022/11/msg00000.html) and [the maintainer's reply](https://lists.debian.org/debian-dpkg/2022/11/msg00006.html) | A first-hand example of the naming discussion: the name need not match other distributions or the GNU triplet; append the bit width; omit endianness when the architecture is effectively single-endian. | Nov 2022, **old**, still the best precedent |
| [dh_update_autotools_config(1)](https://manpages.debian.org/testing/debhelper/dh_update_autotools_config.1.en.html) and [autotools-dev](https://tracker.debian.org/pkg/autotools-dev) | Replaces each package's `config.sub` and `config.guess` with the newer copies from `autotools-dev`. So the new triplet has to be added to `autotools-dev` (and to GNU config upstream) before packages' configure scripts accept it. | current |
| [Debian Policy 11.1](https://www.debian.org/doc/debian-policy/ch-customized-programs.html) and [3.8 (Essential packages)](https://www.debian.org/doc/debian-policy/ch-binary.html) | Architecture specification strings and wildcards; what Essential means. | Policy 4.7.4.1 |
| [BuildProfileSpec](https://wiki.debian.org/BuildProfileSpec) | The build-profile specification and the registry of well-known profiles (`cross`, `nocheck`, `nodoc`, `nobiarch`, `noudeb`, ...). The `stage1` and `stage2` profiles are deprecated. | 2026-08-16 |

### Cross-building and toolchain bootstrap

| Page | What it contains | Date / status |
|---|---|---|
| [CrossBuildPackagingGuidelines](https://wiki.debian.org/CrossBuildPackagingGuidelines) | How to make packages cross-buildable: Salsa CI cross-build test, hints, the `ftcbfs` bug tag, `CONFIG_SITE` cache files for autoconf, open issues. | 2025-12-11, current |
| [MultiarchCrossToolchainBootstrap](https://wiki.debian.org/MultiarchCrossToolchainBootstrap) | The staged gcc and glibc bootstrap for an architecture that does not exist in the archive yet, with real commands (mips64el as the example). | 2015-05-11, **old** (gcc-5 era) |
| [MultiarchCrossToolchainBuild](https://wiki.debian.org/MultiarchCrossToolchainBuild) | Cross-binutils, cross-gcc, `crossbuild-essential`. Notes that LLVM can cross-compile with standard packages but "lacks encoded Debian ABI defaults". | 2015-05-23, **old** |
| [ReleaseGoals/CrossBuildableBase](https://wiki.debian.org/ReleaseGoals/CrossBuildableBase) | The goal of making the roughly 140 base packages cross-buildable. | 2014-04-23, **old** |

### Mailing lists and channels

- [debian-cross](https://lists.debian.org/debian-cross/): "How to use cross-builds to bootstrap Debian ports"; active (archives 2013 to November 2026). This is the main list for bootstrapping questions.
- `#debian-bootstrap` and `#debian-ports` on OFTC: named on the wiki pages; we did not connect to confirm them.
- There is no active debian-ports mailing list (its archive has only January 2008). Port-specific lists exist, such as [debian-riscv](https://lists.debian.org/debian-riscv/) and [debian-loongarch](https://lists.debian.org/debian-loongarch/).
- [Bootstrap sprint, Paris 2014](https://wiki.debian.org/Sprints/2014/BootstrapSprint/Results) (**old**): early bootstrapping without a Packages file, cross-toolchain naming, build-profile semantics. [The 2025 Würzburg sprint page](https://wiki.debian.org/Sprints/2025/BootstrapCrossbuild) has an agenda but no results (**uncertain**).

## 2. Case studies and talks

**riscv64** (the best first-hand material):
- Manuel A. Fernandez Montecelo, [Debian GNU/Linux port for RISC-V 64-bit](https://people.debian.org/~mafm/posts/2017/20170422_debian-gnulinux-port-for-risc-v-64-bit-riscv64) (2017-04-22, **old**): a private repository of about 1,000 source packages, cross-built with rebootstrap, then rebuilt natively. Pitfalls: toolchain ABI churn, copyright assignment delaying upstreaming, very limited QEMU.
- The same author, [riscv64 in Debian infrastructure (debian-ports)](https://people.debian.org/~mafm/posts/2018/20180402_debian-gnulinux-port-for-risc-v-64-bit-riscv64-in-debian-infrastructure-debian-ports/) (2018-04-02, **old**): the actual recipe, in order: cross-compile a base set; build "native-1" under qemu-system; build a minimal "native-2" seed; import it into debian-ports; automate the buildds; break cycles by hand. The best written recipe we found.
- Aurelien Jarno, [riscv64 becomes official](https://lists.debian.org/debian-riscv/2023/07/msg00053.html) (2023-07-23): the promotion step, rebootstrapped inside the official archive from about 90 minimal source packages.
- [RISC-V on the wiki](https://wiki.debian.org/RISC-V) and [Ports/riscv64](https://wiki.debian.org/Ports/riscv64): hardware, cross toolchains, QEMU setup, porterbox, history from 2016.

**loong64:**
- Zhang Dandan, [the proposal on debian-devel](https://lists.debian.org/debian-devel/2022/11/msg00027.html) (2022-11-03, **old**): upstream support merged first, then the opening email. A good template.
- John Paul Adrian Glaubitz, [loong64 is official for 14](https://lists.debian.org/debian-devel/2025/12/msg00165.html) (2025-12-20): 112 hand-built packages imported for the initial chroot, then one buildd built 300 packages overnight.
- [Ports/loong64](https://wiki.debian.org/Ports/loong64) (2026-03-31), [LoongArch](https://wiki.debian.org/LoongArch) (2026-09-10), and Freexian's [Debian contributions, November 2025](https://www.freexian.com/blog/debian-contributions-11-2025/) (rebootstrap used for the initial package set).

**arm64:** [Arm64Port](https://wiki.debian.org/Arm64Port) (bring-up history: a personal repository of about 350 source packages, official in Jessie); Wookey's [FOSDEM 2013 talk](https://archive.fosdem.org/2013/schedule/event/debian_arm64_bootstrap/) and Johannes Schauer's [FOSDEM 2013 talk on bootstrapping Debian-based distributions for new architectures](https://archive.fosdem.org/2013/schedule/event/debian_bootstrap/) (both **old**).

**Process talks:** Nathan Willis, [Automating architecture bootstrapping in Debian](https://lwn.net/Articles/656986/) (LWN, 2015, **old** but still conceptually accurate); the [Cross Building slides](https://get.debian.org/pub/debian-meetings/2024/MiniDebConf-Toulouse/slides/toulouse2024-12-cross-building.pdf) from MiniDebConf Toulouse 2024 (**uncertain**: the text could not be read); the [DebConf19 Bootstrappable Debian BoF notes](https://gobby.debian.org/export/debconf19/bof/bootstrappable_debian_bof) (2019, **old**).

**Other ports, mostly as warnings:** [Sparc64](https://wiki.debian.org/Sparc64) (install with a patched debootstrap); [hurd-amd64](https://wiki.debian.org/Ports/hurd-amd64); Aurelien Jarno's [Goodbye Debian GNU/kFreeBSD](https://blog.aurel32.net/goodbye-kfreebsd.html) (2023): a first-hand account of why a port dies, worth reading as a failure case.

## 3. The pieces outside Debian that a Debian port depends on

- **Linux kernel.** Joël Porquet, [Porting Linux to a new processor architecture, part 1](https://lwn.net/Articles/654783/) (LWN, 2015-08-26, **old** but still the best narrative: the `arch/` skeleton, Kconfig, early console, stubbing until it boots) and his [Kernel Recipes slides](https://www.slideshare.net/slideshow/kernel-recipes-2015-porting-linux-to-a-new-processor-architecture/53697413). There is **no official "new architecture" guide** in the kernel documentation. [Building Linux with LLVM](https://docs.kernel.org/kbuild/llvm.html) (`make LLVM=1`) lists the architectures supported with clang today (arm, arm64, riscv, x86) and the ones maintained (hexagon, loongarch, mips, powerpc, um). [ClangBuiltLinux](https://clangbuiltlinux.github.io/) tracks the status.
- **glibc.** The glibc wiki page `NewPorts` and the manual's porting chapter could not be fetched (the server blocked automated reads), so what follows is **uncertain**: new ports go through `libc-alpha`, the test suite must pass, the port lives in `sysdeps/<arch>`, and binutils, GCC and the kernel must be upstream first. Open <https://www.sourceware.org/glibc/wiki/NewPorts> in a browser. On building glibc with clang: MaskRay, [When can glibc be built with Clang?](https://maskray.me/blog/2021-10-10-when-can-glibc-be-built-with-clang) (updated 2026) lists the blockers; glibc 2.43 reportedly adds experimental Clang support for aarch64 and x86_64 (**uncertain**: from search summaries only).
- **GCC and binutils.** [Anatomy of a Target Back End](https://gcc.gnu.org/onlinedocs/gccint/Back-End.html) in the GCC internals manual. We found no binutils porting manual by fetch.
- **LLVM.** [Writing an LLVM Backend](https://llvm.org/docs/WritingAnLLVMBackend.html) (current): the compiler back end only, not the clang driver or the ABI.
- **Debian and clang.** [llvm-clang](https://wiki.debian.org/llvm-clang) (2013) and [ReleaseGoals/clang-secondary-compiler](https://wiki.debian.org/ReleaseGoals/clang-secondary-compiler) (2014) are both **old**: they record rebuilding packages with clang, not porting an architecture with it. We found no Debian port, and no documented attempt, that is clang-only.

## 4. A minimal Debian

- [mmdebstrap(1)](https://manpages.debian.org/testing/mmdebstrap/mmdebstrap.1.en.html): variants `essential`, `required` (the same as `minbase`), `buildd` and others; `--variant=custom` installs only what you name and has a chrootless mode. No `--foreign` stage; it relies on QEMU binfmt.
- [debootstrap(8)](https://manpages.debian.org/testing/debootstrap/debootstrap.8.en.html): `--variant=minbase` is the required-priority packages plus apt; `buildd` adds `build-essential`; `--foreign` and `--second-stage` split the run, which is what a new CPU needs when you cannot chroot natively.
- [BootstrapBootableSystem](https://wiki.debian.org/BootstrapBootableSystem) (2026-11-01): a bootable x86 system from mmdebstrap with a kernel, a boot loader and ssh; shows the shape of the result, not another CPU. [EmDebian/CrossDebootstrap](https://wiki.debian.org/EmDebian/CrossDebootstrap): four ways to make a root file system for another CPU (**uncertain**: mixed age).

## What we could not find

- A current, command-by-command guide to bringing Debian up on a new architecture.
- Any Debian port bootstrapped without GCC, or any statement that Debian will accept an architecture whose only compiler is LLVM.
- A Linux "add a new architecture" document in the kernel tree (only the 2015 LWN material).
- The glibc `NewPorts` page and the manual's porting chapter, a binutils porting guide, and the GNU config contribution process (not read).
- The `rebootstrap` README (not read), a recent first-hand bring-up of ppc64el, mips64el or sparc64, and the `botch` tool's current home.

## What this means for the pdp64

The dpkg requirement makes the compiler decision in [the plan](../PLAN.md) bigger than it looked: an architecture name in dpkg wants upstream GCC and binutils support, and our back end is LLVM. The realistic options are a GCC back end, or an unofficial port that keeps its own private `dpkg` tables until upstream support exists, which is what the riscv64 port did in its early years. That choice is still open.
