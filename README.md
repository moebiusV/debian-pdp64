# Debian on the pdp64

A port of Debian 13 ("trixie") to the [pdp64](https://moebiusv.github.io/pdp64/), a 64-bit successor to the PDP-11: the smallest bootable Debian system you can ssh into, and the plan for it.

- [The plan](PLAN.md): what the system is, what must be ready before it can boot, and in what order.
- [The minimal system](docs/minimal-system.md): the packages it consists of, measured from Debian's signed archive indexes.
- [Porting resources](docs/porting-resources.md): everything we could find on bringing Debian up on a new CPU architecture, collected in one place.

The OpenBSD port ([openbsd-pdp64](https://moebiusv.github.io/openbsd-pdp64/)) comes first; this one starts after it is running.
