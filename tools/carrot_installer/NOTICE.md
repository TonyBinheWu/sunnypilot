# C4 compatibility installer

`build.py` embeds the unmodified C4 ELF served by sunnypilot's official fork
installer service for TonyBinheWu/carrot-wip with device header `mici`.
Its exact SHA-256 is pinned; a service update fails the build until inspected.
The original URL, device header, hash and this checkout's source commit appear
in each distribution's manifest. The payload is inspected, never executed on
the build host. The resulting entry is static aarch64 Linux ELF for C4 only.

This repository's LICENSE applies to the compatibility source. The embedded
installer is part of the openpilot/sunnypilot installer family; its notices and
upstream licensing remain applicable. Source references:

- https://github.com/sunnypilot/openpilot-installer-generator
- https://github.com/commaai/openpilot/tree/master/selfdrive/ui/installer
- This checkout: `openpilot/selfdrive/ui/installer/installer.cc`

The compatibility preflight changes only a marked `/data/openpilot` factory
cache's origin when `/data/continue.sh` is absent. It does not delete the cache,
reset settings, grant access or retry a failed installation. The upstream child
performs the existing requested installation. Child failure and missing/invalid
handoff return a nonzero result with a persistent stage file and log. This entry
cannot change the factory setup program's own retry behavior.

The `openpilot.git` URL embedded by the official C4 payload currently redirects
to TonyBinheWu/sunnypilot. The preflight uses the canonical sunnypilot URL.
The branch-installed source separately fixes cachedFetch to retarget its copy
before fetching; that source change alone cannot repair an older external ELF.
