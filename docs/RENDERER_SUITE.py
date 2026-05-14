"""
PVIEW FULL RENDERER SUITE - IMPLEMENTATION COMPLETE

This document catalogs the 27 specialized renderers built for pview, plus the TextRenderer fallback.
Each renderer displays a specific /proc file or directory with human-readable,
educational formatting instead of raw text output.

═══════════════════════════════════════════════════════════════════════════════
"""

# CATEGORY 1: PROCESS STATE & SCHEDULING (5 RENDERERS)
# ─────────────────────────────────────────────────

"""
📊 StatRenderer - /proc/[pid]/stat
   Status: ✅ COMPLETE
   Files: src/pview/renderers/stat_renderer.py
   What: Decodes 50+ scheduling fields
   Output:
     • State (R/S/D/Z/T/W/X with meaning)
     • Parent PID
     • CPU times (jiffies → seconds)
     • Virtual/resident memory
   Example: Shows "991 (pipewire) is Running, 2.34s user time, 128 MiB VmSize"

📋 StatmRenderer - /proc/[pid]/statm
   Status: ✅ COMPLETE
   Files: src/pview/renderers/statm_renderer.py
   What: Memory summary in page units
   Output:
     • Total VM size (KiB → MiB)
     • RSS (resident memory)
     • Shared pages
     • Code, libraries, data breakdown
   Example: "RSS 45 MiB / 128 MiB total, 8 MiB shared libraries"

🔍 StatusRenderer (ENHANCED) - /proc/[pid]/status
   Status: ✅ ENHANCED with 17 fields + descriptions
   Files: src/pview/renderers/status_renderer.py (modified)
   What: Comprehensive process snapshot
   New Fields: UID/GID, Threads, Swap, Seccomp, Signals
   Example: Shows Name, PID, State, Memory, Security context, etc.

🔧 CmdlineRenderer - /proc/[pid]/cmdline
   Status: ✅ COMPLETE (existing)
   What: Command + indexed arguments
   Output: Parses null-terminated args into clean display

🌍 EnvironRenderer - /proc/[pid]/environ
   Status: ✅ COMPLETE (existing)
   What: Environment variables
   Output: KEY=value with smart truncation
"""

# CATEGORY 2: RESOURCE LIMITS & OOM (4 RENDERERS)
# ─────────────────────────────────────────────

"""
⚙️ LimitsRenderer - /proc/[pid]/limits
   Status: ✅ COMPLETE
   Files: src/pview/renderers/limits_renderer.py
   What: Resource constraints (soft/hard limits)
   Output:
     • Max open files, stack size, memory, CPU time
     • Soft limit vs Hard limit side-by-side
     • Shows "unlimited" for unbounded limits
   Example: "Max files: 1024 (soft) / 65536 (hard)"

💀 OomScoreRenderer - /proc/[pid]/oom_score
   Status: ✅ COMPLETE
   Files: src/pview/renderers/oom_score_renderer.py
   What: Kernel's OOM killer priority (0-1000+)
   Output:
     • Score value
     • Risk level (Low/Medium/High/Very High)
     • Color-coded by danger
   Example: "Score 234 = High kill risk (orange)"

🔧 OomScoreAdjRenderer - /proc/[pid]/oom_score_adj
   Status: ✅ COMPLETE
   Files: src/pview/renderers/oom_score_adj_renderer.py
   What: User-adjustable OOM priority offset (-1000 to 1000)
   Output:
     • Adjustment value
     • Resulting priority level
     • Explanation of adjustability
   Example: "Adj -100 = Low priority, protected from OOM killer"
"""

# CATEGORY 3: SYSTEM ISOLATION & SECURITY (4 RENDERERS)
# ─────────────────────────────────────────────────────

"""
🔒 NamespacesRenderer - /proc/[pid]/ns/
   Status: ✅ COMPLETE
   Files: src/pview/renderers/namespaces_renderer.py
   What: Container/process isolation info
   Output:
     • All namespace types (cgroup, ipc, mnt, net, pid, user, uts, time)
     • Inode numbers (shared inode = shared namespace)
     • Description of each namespace type
   Example: "pid namespace inode 4026531836 (default host)"

🛡️ AttrRenderer - /proc/[pid]/attr/
   Status: ✅ COMPLETE
   Files: src/pview/renderers/attr_renderer.py
   What: SELinux security attributes
   Output:
     • Current context
     • Exec/fscreate/keycreate/prev/sockcreat contexts
     • Only visible if SELinux enabled
   Example: "Type: user_t_r:user_t (unprivileged user process)"

📦 CgroupRenderer - /proc/[pid]/cgroup
   Status: ✅ COMPLETE
   Files: src/pview/renderers/cgroup_renderer.py
   What: Cgroup membership hierarchies
   Output:
     • Hierarchy ID : Subsystems : Path in cgroup
     • Shows controllers (cpu, memory, pids, etc.)
     • Path shows group name
   Example: "[1] cpuset : cpu,cpuacct : /user.slice/user-1000.slice"

🗂️ MountinfoRenderer - /proc/[pid]/mountinfo
   Status: ✅ COMPLETE
   Files: src/pview/renderers/mountinfo_renderer.py
   What: Filesystem mounts visible to process
   Output:
     • Mount ID and point
     • Filesystem type
     • Shows namespace-specific mounts
   Example: "/ (ext4), /dev (tmpfs), /run (tmpfs)"
"""

# CATEGORY 4: MEMORY ANALYSIS (3 RENDERERS)
# ──────────────────────────────────────────

"""
🧠 MapsRenderer - /proc/[pid]/maps
   Status: ✅ COMPLETE (existing)
   What: Memory region layout with permission flags
   Output: 
     • Address ranges
     • [X] executable, [W] writable, [R] readable flags
     • File/library names

📍 SmapsRenderer - /proc/[pid]/smaps
   Status: ✅ COMPLETE
   Files: src/pview/renderers/smaps_renderer.py
   What: Detailed PSS-based memory breakdown
   Output:
     • Total PSS (Proportional Set Size)
     • Per-region Size, RSS, PSS, Swap, etc.
     • PSS accounts for shared pages fairly
   Example: "Total PSS 42 MiB (RSS alone would be 65 MiB due to sharing)"

🏗️ NumaMapsRenderer - /proc/[pid]/numa_maps
   Status: ✅ COMPLETE
   Files: src/pview/renderers/numa_maps_renderer.py
   What: NUMA node memory distribution
   Output:
     • Virtual address ranges
     • Which NUMA nodes hold pages
     • Memory locality information
   Example: "0x400000: node0=128 node1=64 (128 pages on node0, 64 on node1)"
"""

# CATEGORY 5: PROCESS ACTIVITY & SOCKETS (8 RENDERERS)
# ───────────────────────────────────────────

"""
🧵 TaskRenderer - /proc/[pid]/task/
   Status: ✅ COMPLETE
   Files: src/pview/renderers/task_renderer.py
   What: Thread listing for a process
   Output: Per-thread IDs, state, CPU use, and details

🌐 NetTcpRenderer - /proc/[pid]/net/tcp
   Status: ✅ COMPLETE
   Files: src/pview/renderers/net_tcp_renderer.py
   What: TCP socket table for the process namespace
   Output: Local/remote addresses, state, and queue information

🌐 NetUdpRenderer - /proc/[pid]/net/udp
   Status: ✅ COMPLETE
   Files: src/pview/renderers/net_udp_renderer.py
   What: UDP socket table
   Output: Local/remote addresses and queue information

🌐 NetUnixRenderer - /proc/[pid]/net/unix
   Status: ✅ COMPLETE
   Files: src/pview/renderers/net_unix_renderer.py
   What: UNIX socket table
   Output: Socket paths and metadata

🌐 NetDevRenderer - /proc/[pid]/net/dev
   Status: ✅ COMPLETE
   Files: src/pview/renderers/net_dev_renderer.py
   What: Network interface counters
   Output: RX/TX bytes, packets, drops, and errors per interface

📈 IoRenderer - /proc/[pid]/io
   Status: ✅ COMPLETE (existing)
   What: I/O statistics
   Output: Read/write counts, bytes, syscalls

📊 SchedRenderer - /proc/[pid]/sched
   Status: ✅ COMPLETE (existing)
   What: Scheduler details
   Output: Context switches, time slices, priority

📂 FdRenderer - /proc/[pid]/fd/
   Status: ✅ COMPLETE (existing)
   What: File descriptors
   Output:
     • FD number
     • Type and access flags
     • Resolved path (symlink target)
   Example: "3 → /dev/pts/1 (character device, rw)"

🔗 SymlinkRenderer - /proc/[pid]/exe, cwd, root, fd/*, ns/*
   Status: ✅ COMPLETE
   Files: src/pview/renderers/symlink_renderer.py
   What: Resolves proc symlink targets with path meaning
   Output: Human-readable symlink destinations and explanations
"""

# CATEGORY 6: SYSTEM-WIDE (2 RENDERERS)
# ──────────────────────────────────────

"""
💾 MemInfoRenderer - /proc/meminfo
   Status: ✅ COMPLETE (existing)
   What: System memory statistics
   Output:
     • Memory bars with percentages
     • Human-readable units
     • Free, used, cached, swap

🔌 CpuInfoRenderer - /proc/cpuinfo
   Status: ✅ COMPLETE (existing)
   What: CPU topology and capabilities
   Output:
     • Physical/logical CPU counts
     • Frequencies, cache sizes
     • Supported features
"""

# CATEGORY 7: ADVANCED (2 RENDERERS)
# ──────────────────────────────────

"""
💥 CoredumpFilterRenderer - /proc/[pid]/coredump_filter
   Status: ✅ COMPLETE
   Files: src/pview/renderers/coredump_filter_renderer.py
   What: Core dump bitmask settings
   Output:
     • Hex value decoded
     • Checkbox per memory region type
     • Shows which regions included in crash dumps
   Example: "0x33 = Include: anonymous memory, shared mem, text, elf libraries"

📄 TextRenderer - Fallback
   Status: ✅ COMPLETE (existing)
   What: Renders unmapped file types
   Output: Plain formatted text
"""

# REGISTRY STRUCTURE
# ──────────────────

"""
RendererRegistry (src/pview/renderers/registry.py)
   Total Renderers: 28
   Specialized Renderers: 27
   
   Dispatch Order:
   1. StatRenderer              (most specific)
   2. StatmRenderer
   3. StatusRenderer
   4. CmdlineRenderer
   5. EnvironRenderer
   6. LimitsRenderer
   7. NamespacesRenderer
   8. OomScoreRenderer
   9. OomScoreAdjRenderer
   10. MountinfoRenderer
   11. CoredumpFilterRenderer
   12. SmapsRenderer
   13. NumaMapsRenderer
   14. AttrRenderer
   15. CgroupRenderer
   16. TaskRenderer
   17. NetTcpRenderer
   18. NetUdpRenderer
   19. NetUnixRenderer
   20. NetDevRenderer
   21. SymlinkRenderer
   22. FdRenderer
   23. MapsRenderer
   24. IoRenderer
   25. SchedRenderer
   26. MemInfoRenderer
   27. CpuInfoRenderer
   28. TextRenderer             (fallback)
   
   Selects first renderer where can_render(path) returns True.
   TextRenderer always returns True as safety net.
"""

# USAGE EXAMPLES
# ──────────────

"""
Launch pview and navigate:

/proc                           (root)
├─ 1                            (PID 1 - systemd process)
│  ├─ stat                       → StatRenderer: "Running, 2.3s user, 1.1s system"
│  ├─ statm                      → StatmRenderer: "RSS 12 MiB / VmSize 128 MiB"
│  ├─ status                     → StatusRenderer: 17 fields with context
│  ├─ fd                         → FdRenderer: "3→/dev/pts/1, 4→/proc"
│  ├─ maps                       → MapsRenderer: "[X] 0x400000-0x500000 /bin/systemd"
│  ├─ io                         → IoRenderer: "read 1.2GB, write 45MB"
│  ├─ limits                     → LimitsRenderer: "Max files: 1024 (soft) / unlimited"
│  ├─ ns/
│  │  └─ pid                     → NamespacesRenderer: "inode 4026531836 (shared)"
│  ├─ cgroup                     → CgroupRenderer: "[1] cpuset : cpu,cpuacct"
│  └─ oom_score                  → OomScoreRenderer: "Score 5 (Very Low risk)"
├─ meminfo                       → MemInfoRenderer: Memory bars
└─ cpuinfo                       → CpuInfoRenderer: CPU topology

Each renderer provides human-readable output with:
  • Unit conversions (jiffies→seconds, pages→MiB)
  • Contextual explanations
  • Color coding where relevant
  • Graceful error handling
"""

# TESTING
# ───────

"""
Run tests:
  pytest tests/test_renderers.py -xvs
  
Tests verify:
   ✓ All 27 specialized renderers instantiate correctly
  ✓ Each renderer's can_render() method matches correct paths
  ✓ Registry initialization complete
  ✓ No import errors

Test file: tests/test_renderers.py (27 detection tests)
"""

print(__doc__)
