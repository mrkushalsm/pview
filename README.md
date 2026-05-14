# pview

> A terminal-native explorer for Linux `/proc` that turns raw kernel files into readable, context-rich panels.

pview is built for the parts of `/proc` that are hard to inspect with plain `cat`: symlinks, tables, key/value snapshots, per-thread views, and permission-sensitive entries. Instead of dumping raw text, it renders each file in a shape that explains what the kernel is actually saying.

## Highlights

- 27 specialized renderers plus a smart fallback for unmapped files.
- Symlink-aware views for `exe`, `cwd`, `root`, `fd/*`, and `ns/*`.
- Centered sudo prompt with cached authentication for protected entries.
- Async Textual UI with Rich-powered panels, tables, and summaries.
- Clear separation between reading, rendering, and UI layers.

## Quick Start

```bash
python -m pip install -e .
pview
```

## What It Shows

- Process state, CPU time, memory, and command line details.
- Resource limits, OOM scores, cgroups, namespaces, and mounts.
- Memory maps, smaps, NUMA layout, I/O stats, and scheduler data.
- System-wide views like `meminfo` and `cpuinfo`.

## Documentation

- [Linux /proc Filesystem Reference](docs/PROC_FILESYSTEM_REFERENCE.md) for file-by-file explanations and renderer guidance.
- [Implementation Report](docs/IMPLEMENTATION_REPORT.md) for the renderer suite breakdown and delivery summary.

## Project Layout

- `src/pview/core/` handles procfs reading, retry logic, and permission recovery.
- `src/pview/renderers/` contains the specialized renderers and smart fallback rendering.
- `src/pview/widgets/` contains the Textual widgets and modal UI.
- `src/pview/models/` contains the domain objects used by the explorer.
- `src/pview/utils/` contains shared helpers.

## Why It’s Structured This Way

`/proc` is not a normal filesystem. Some entries are fixed-format records, some are tables, some are symlinks, and some vanish while you are reading them. Keeping the reader, renderer, and UI concerns separate makes the explorer easier to extend without destabilizing the interface.
