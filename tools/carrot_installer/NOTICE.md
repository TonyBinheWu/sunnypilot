# C4 compatibility installer

**V1/v2 are retired.** The affected C4 still returned to Start before an
Installing UI. Both wrappers embed the same Wayland installer; cache-only
tests do not validate that graphical runtime. The current official installer
uses `/tmp/drmfd.sock` and has its own copied-cache origin fix. Use
`TonyBinheWu/carrot-wip` in the C4 setup URL field, which expands to
`https://installer.comma.ai/TonyBinheWu/carrot-wip`.

`verify_official.py` checks the actual fetched ELF's architecture, DT_NEEDED,
display contract, fork/branch and cache command without executing it. CI now
uploads that verification report instead of rebuilding old wrappers. Historical
reproduction requires `build.py --historical-reproduction`; no physical-device
acceptance is implied by inspection or CI.

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

Version 2 parks only the factory-cache marker when `/data/continue.sh` is absent,
so the child fresh-clones. It never runs Git against or writes into the original
cache, which can be read-only or owned by another user. Failure restores the
marker with atomic no-overwrite rename; competing changes preserve its parked
copy. Success removes only the parked marker. It does not delete the cache,
reset settings, grant access or retry a failed installation. The upstream child
performs the existing requested installation. Child failure and missing/invalid
handoff return a nonzero result with a persistent stage file and log. This entry
cannot change the factory setup program's own retry behavior.

The `openpilot.git` URL embedded by the official C4 payload currently redirects
to TonyBinheWu/sunnypilot. The copied-cache source fix uses the configured fork URL.
The branch-installed source separately fixes cachedFetch to retarget its copy
before fetching; that source change alone cannot repair an older external ELF.
