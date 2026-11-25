# How this repository is laid out

The repository holds only what the port adds or changes; Debian's own sources and packages are fetched
from the archive, not stored here.

| | |
|---|---|
| `BASE` | the Debian release the port is made against (suite, point release, signed Release date and hash) |
| `overlay/` | new files, one directory per source package |
| `patches/` | changes to files Debian's source packages have, one directory per source package |
| `tools/fetch-indexes.sh` | fetch the package indexes of trixie into `./cache` (git-ignored), checked against the signed Release |
| `tools/closure.py` | the package set of the minimal system, from those indexes; prints the report that `docs/minimal-system.md` is made from |

The tools to apply the overlay to source packages come when there is something to apply.
