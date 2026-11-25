#!/usr/bin/env python3
"""The package set of a minimal bootable Debian you can ssh into, measured from the signed archive indexes.

usage: closure.py PACKAGES SOURCES      (the unpacked Packages and Sources of dists/trixie/main, amd64)
Roots: every Essential package, apt, openssh-server, iproute2, and one init system.  Dependencies are followed
the way debootstrap does it, first alternative first, a provider for a virtual package.  The kernel is not in
the set (it is ours).  Prints a markdown report.
"""
import re, sys, collections

def paras(path):
    for p in open(path, encoding='utf-8', errors='replace').read().split('\n\n'):
        d, key = {}, None
        for line in p.split('\n'):
            if line[:1] in ' \t' and key:
                d[key] += '\n' + line
            elif ':' in line:
                key, v = line.split(':', 1); d[key] = v.strip()
        if 'Package' in d:
            yield d

pk = {d['Package']: d for d in paras(sys.argv[1])}
src = {d['Package']: d for d in paras(sys.argv[2])}
prov = collections.defaultdict(list)
for n, d in pk.items():
    for x in d.get('Provides', '').split(','):
        x = x.strip().split(' ')[0]
        if x: prov[x].append(n)

def deps(d):
    out = []
    for fld in ('Pre-Depends', 'Depends'):
        for grp in d.get(fld, '').split(','):
            alts = [re.sub(r'[ (:].*', '', a.strip()) for a in grp.split('|') if a.strip()]
            if alts: out.append(alts)
    return out

def closure(roots):
    have, todo = set(), list(roots)
    while todo:
        n = todo.pop()
        if n in have or n not in pk: continue
        have.add(n)
        for alts in deps(pk[n]):
            if any(a in have for a in alts): continue
            for a in alts:
                if a in pk: todo.append(a); break
                if a in prov: todo.append(prov[a][0]); break
    return have

ess = [n for n, d in pk.items() if d.get('Essential') == 'yes']
base = ess + ['apt', 'openssh-server', 'iproute2']
variants = {'systemd': base + ['systemd-sysv'], 'sysvinit': base + ['sysvinit-core']}

def srcname(n):
    return pk[n].get('Source', n).split(' ')[0]

print(f"Essential packages: {len(ess)}\n")
print("| variant | binary packages | architecture-dependent | architecture-independent | source packages to build for the pdp64 |")
print("|---|---:|---:|---:|---:|")
res = {}
for v, roots in variants.items():
    c = closure(roots)
    anyarch = [n for n in c if pk[n].get('Architecture') != 'all']
    srcs = sorted({srcname(n) for n in anyarch})
    res[v] = (c, anyarch, srcs)
    print(f"| {v} | {len(c)} | {len(anyarch)} | {len(c)-len(anyarch)} | {len(srcs)} |")
c, anyarch, srcs = res['systemd']
size = sum(int(pk[n].get('Installed-Size', 0)) for n in c)
print(f"\nInstalled size of the systemd variant: {size/1024:.0f} MB.\n")
print("Source packages of the systemd variant, with the architecture-dependent binaries each makes:\n")
by = collections.defaultdict(list)
for n in anyarch: by[srcname(n)].append(n)
for s in srcs:
    print(f"- `{s}`: " + ', '.join(f"`{b}`" for b in sorted(by[s])))
print("\nThe systemd variant has these that sysvinit has not, and the other way round:")
print("- only systemd: " + ', '.join(sorted(res['systemd'][0] - res['sysvinit'][0])[:40]))
print("- only sysvinit: " + ', '.join(sorted(res['sysvinit'][0] - res['systemd'][0])[:40]))
