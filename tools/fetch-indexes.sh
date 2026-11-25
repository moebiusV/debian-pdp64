#!/bin/sh
# Fetch the package indexes of Debian trixie (main, amd64 and source) into ./cache, checking them against the
# signed InRelease (gpgv with the archive keyring) and its SHA256 list.  Prints the two paths for closure.py.
set -eu
ROOT=$(cd "$(dirname "$0")/.." && pwd); C=$ROOT/cache; B=${DEBIAN_MIRROR:-https://deb.debian.org/debian}/dists/trixie
KR=/usr/share/keyrings/debian-archive-keyring.pgp
mkdir -p "$C"; cd "$C"
curl -sf -o InRelease "$B/InRelease"
gpgv --keyring "$KR" InRelease 2>&1 | grep -q 'Good signature' || { echo "InRelease signature not good" >&2; exit 1; }
for f in main/binary-amd64/Packages.xz main/source/Sources.xz; do
    want=$(awk -v f="$f" '/^SHA256:/{s=1;next} /^[A-Za-z]/{s=0} s&&$3==f{print $1; exit}' InRelease)
    curl -sf -o "$(basename "$f")" "$B/$f"
    [ "$(sha256sum "$(basename "$f")" | cut -d' ' -f1)" = "$want" ] || { echo "$f does not match the signed Release" >&2; exit 1; }
    xz -dkf "$(basename "$f")"
done
echo "$C/Packages $C/Sources"
