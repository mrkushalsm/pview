# Linux /proc/[pid]/ Filesystem Reference
## Complete Guide for Process Rendering

---

## 1. **stat** (Regular File)
### Purpose
Process scheduling statistics from the kernel scheduler. Core performance and resource data.

### Format
Single line with space-separated fields:
```
pid (comm) state ppid pgrp session tty_nr tpgid flags minflt cminflt majflt cmajflt 
utime stime cutime cstime priority nice num_threads itrealvalue starttime vsize rss 
rsslim ... (up to 52 fields in modern kernels)
```

### Key Fields to Extract
| Field | Meaning | Example |
|-------|---------|---------|
| **pid** | Process ID | 1234 |
| **comm** | Command name (truncated to 15 chars, parenthesized) | (bash) |
| **state** | Process state | R=running, S=sleeping, D=disk sleep, Z=zombie, T=stopped |
| **ppid** | Parent process ID | 1 |
| **pgrp** | Process group ID | 1234 |
| **session** | Session ID | 1 |
| **tty_nr** | Controlling terminal (major,minor) | 0 (no tty) or dev_major*256+dev_minor |
| **tpgid** | Foreground process group of tty | -1 (not in foreground) |
| **flags** | Process flags (bitmap) | 1=forked, 4=traced, etc. |
| **minflt** | Minor page faults | 1523 |
| **cminflt** | Minor page faults (children) | 45 |
| **majflt** | Major page faults | 12 |
| **cmajflt** | Major page faults (children) | 2 |
| **utime** | User-mode time (jiffies) | 234 |
| **stime** | Kernel-mode time (jiffies) | 56 |
| **cutime** | User-mode time (children, jiffies) | 100 |
| **cstime** | Kernel-mode time (children, jiffies) | 20 |
| **priority** | Scheduler priority (kernel) | 20 |
| **nice** | Nice value (user adjustable) | 0 |
| **num_threads** | Number of threads | 4 |
| **starttime** | Time process started (jiffies since boot) | 234567 |
| **vsize** | Virtual memory size (bytes) | 2458624 |
| **rss** | Resident set size (pages) | 512 |

### Format Details
- Times in **jiffies** (1/CONFIG_HZ per jiffie, typically 10ms)
- Convert to seconds: `jiffies / sysconf(_SC_CLK_TCK)`
- `starttime` is in jiffies since boot: combine with `/proc/uptime` to get wall-clock start time
- Page size is 4096 bytes on most systems
- Flags: bitmap combining permission bits

### Human-Readable Meaning
This file is the **quick snapshot** of what a process is doing right now:
- State tells if it's running, sleeping, or stuck
- utime/stime shows CPU usage (convert to percentage with uptime)
- vsize/rss shows memory footprint
- num_threads shows parallelism
- Priority shows scheduling importance

### Example
```
1234 (python) S 1 1234 1234 0 -1 4194304 5234 0 0 0 234 56 0 0 20 0 4 0 45678 2458624 512 18446744073709551615 ...
```
**Interpretation:**
- PID 1234 running python in sleeping state
- Parent is 1234 (process group leader)
- 4 threads active
- Used ~5GB virtual memory, ~2MB resident
- 234 jiffies user time, 56 jiffies kernel time (~3 seconds total @ 100Hz)
- Started at jiffies 45678 (since boot)

### Renderer Use Case
**CPU & Memory Quick View:** Extract utime, stime, vsize, rss, num_threads for a summary card

---

## 2. **statm** (Regular File)
### Purpose
Memory usage in pages (simpler than stat). Quick memory snapshot.

### Format
Seven space-separated fields:
```
size resident shared text lib data dt
```

### Key Fields
| Field | Meaning | Typical Value |
|-------|---------|---|
| **size** | Virtual memory size (pages) | 6009 |
| **resident** | Resident set size (pages) | 1234 |
| **shared** | Shared pages (old, usually 0) | 0 |
| **text** | Text segment (code, pages) | 256 |
| **lib** | Library pages (deprecated, usually 0) | 0 |
| **data** | Data + BSS (pages) | 512 |
| **dt** | Dirty pages (usually 0) | 0 |

### Format Details
- All values in **pages** (4096 bytes each on most systems)
- Total RSS in bytes = `resident * 4096`
- Shared memory is rarely tracked here (use `/proc/[pid]/smaps` instead)

### Human-Readable Meaning
**Stripped-down memory view** for when you just need memory numbers:
- resident = actual RAM consumed (excluding swapped/shared)
- size = total addressable memory (including swapped)
- Most modern tools ignore shared/lib/dt

### Example
```
6009 1234 0 256 0 512 0
```
**Interpretation:**
- Virtual: ~24 MB (6009 pages)
- Resident: ~5 MB (1234 pages in RAM)
- Code: ~1 MB
- Data: ~2 MB

### Renderer Use Case
**Memory gauge:** Quick RSS in MB = `resident * 4096 / 1024 / 1024`

---

## 3. **status** (Regular File)
### Purpose
Human-readable process status. Detailed breakdown with field names.

### Format
Key-value pairs (newline-separated):
```
Name:	python
Umask:	0022
State:	S (sleeping)
Tgid:	1234
Ngid:	0
Pid:	1234
PPid:	1
TracerPid:	0
Uid:	1000	1000	1000	1000
Gid:	1000	1000	1000	1000
FDSize:	256
VmPeak:	2485 kB
VmHWM:	1503 kB
VmRSS:	1234 kB
RssAnon:	512 kB
RssFile:	600 kB
RssShmem:	122 kB
VmData:	512 kB
VmStk:	132 kB
VmExe:	200 kB
VmLib:	1024 kB
VmPTE:	50 kB
VmSwap:	0 kB
Threads:	4
SigQ:	0/127657
SigPnd:	0000000000000000
ShdPnd:	0000000000000000
SigBlk:	0000000000000000
SigIgn:	0000000000000000
SigCgt:	0000000000000000
CapInh:	0000000000000000
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	0000003fffffffff
CapAmb:	0000000000000000
NoFile:	65535
NoFileHard:	65535
Seccomp:	0
Cpus_allowed_list:	0-7
Mems_allowed_list:	0
voluntary_ctxt_switches:	1234
nonvoluntary_ctxt_switches:	567
```

### Key Fields to Extract
| Field | Meaning | Example |
|-------|---------|---------|
| **Name** | Command name | python |
| **State** | Process state with description | S (sleeping) |
| **Tgid** | Thread group ID (main PID for threads) | 1234 |
| **Pid** | Process/thread ID | 1234 |
| **PPid** | Parent PID | 1 |
| **TracerPid** | PID of debugger (0 if none) | 0 |
| **Uid** | Real, Effective, Saved, FS UIDs | 1000 1000 1000 1000 |
| **Gid** | Real, Effective, Saved, FS GIDs | 1000 1000 1000 1000 |
| **FDSize** | File descriptor table size | 256 |
| **VmPeak** | Peak virtual memory (kB) | 2485 |
| **VmHWM** | Peak resident set (high water mark, kB) | 1503 |
| **VmRSS** | Current resident set (kB) | 1234 |
| **RssAnon** | Anonymous memory (heap, stack, kB) | 512 |
| **RssFile** | File-backed memory (mmapped files, kB) | 600 |
| **RssShmem** | Shared memory (kB) | 122 |
| **VmData** | Data + BSS (kB) | 512 |
| **VmStk** | Stack (kB) | 132 |
| **VmExe** | Executable code (kB) | 200 |
| **VmLib** | Shared libraries (kB) | 1024 |
| **VmPTE** | Page table entries (kB) | 50 |
| **VmSwap** | Swapped memory (kB) | 0 |
| **Threads** | Number of threads | 4 |
| **SigQ** | Queued signals / limit | 0/127657 |
| **SigPnd** | Pending signals (hex bitmask) | 0000000000000000 |
| **CapEff** | Effective capabilities (hex) | 0000000000000000 |
| **CapBnd** | Capability bounding set (hex) | 0000003fffffffff |
| **NoFile** | Open file descriptor limit | 65535 |
| **Seccomp** | Seccomp mode (0=disabled, 1=strict, 2=filter) | 0 |
| **Cpus_allowed_list** | CPUs this process can use | 0-7 |
| **voluntary_ctxt_switches** | Context switches (voluntary) | 1234 |
| **nonvoluntary_ctxt_switches** | Context switches (forced) | 567 |

### Format Details
- All memory fields in **kilobytes (kB)** = 1024 bytes
- UIDs/GIDs: [real, effective, saved, filesystem]
- Capabilities are hex bitmasks
- Context switches show task aggressiveness
- **HWM** = highest RSS ever reached in this session

### Human-Readable Meaning
**Most user-friendly source** - explains what you need to know:
- State clearly states sleeping/running/zombie/etc.
- Memory broken down by type (anonymous vs file-backed)
- UIDs show who owns this process and under what permissions it runs
- Capability limits and seccomp tell about security restrictions
- Context switches indicate how busy/preempted the process is

### Example
```
Name: python
State: S (sleeping)
Pid: 1234
PPid: 1
Uid: 1000 1000 1000 1000
VmRSS: 1234 kB
Threads: 4
voluntary_ctxt_switches: 1234
```
**Interpretation:**
- Python process sleeping, owned by user 1000
- ~1.2 MB in RAM
- 4 threads, context switched 1234 times voluntarily

### Renderer Use Case
**Detailed Status Panel:** Populate a form with state, UID, memory breakdown, threads, capabilities

---

## 4. **cmdline** (Regular File)
### Purpose
Complete command line that started the process (arguments separated by null bytes).

### Format
Command and arguments separated by **null bytes (`\0`)**, terminated with newline:
```
/usr/bin/python3\0-u\0/home/user/script.py\0--verbose\0
```

### Key Fields
| Component | Meaning | Example |
|-----------|---------|---------|
| **argv[0]** | Executable path or name | /usr/bin/python3 |
| **argv[1]...** | Arguments | -u, /home/user/script.py, --verbose |

### Format Details
- **Null bytes** separate arguments (not spaces!)
- Final newline after last argument
- Empty cmdline = kernel thread (check `/proc/[pid]/comm`)
- If process changed its name (via `prctl(PR_SET_NAME)`), cmdline is unchanged; use `comm` instead

### Human-Readable Meaning
**Exactly what the user typed** (or what started the process):
- Shows full executable path
- Shows all arguments
- Shows current working directory only if executable path is relative
- Compare with `comm` to detect name changes

### Example
```
/usr/bin/python3 -u /home/user/ml_train.py --batch-size 32 --learning-rate 0.001
```
**Interpretation:**
- Python executable from /usr/bin
- Started with -u (unbuffered)
- Running /home/user/ml_train.py
- Custom arguments for batch size and learning rate

### Renderer Use Case
**Command Display:** Parse null-separated args, show in "Command:" field or tooltip; highlight executable and key arguments

---

## 5. **environ** (Regular File)
### Purpose
Environment variables passed to the process at startup.

### Format
Key-value pairs separated by **null bytes**:
```
PATH=/usr/local/bin:/usr/bin:/bin\0
HOME=/home/user\0
LANG=en_US.UTF-8\0
USER=user\0
```

### Key Fields
| Variable | Meaning | Example |
|----------|---------|---------|
| **PATH** | Command search path | /usr/local/bin:/usr/bin:/bin |
| **HOME** | Home directory | /home/user |
| **USER** | Username | user |
| **SHELL** | Login shell | /bin/bash |
| **LANG** | Locale | en_US.UTF-8 |
| **LD_LIBRARY_PATH** | Library search path | /usr/lib:/usr/lib64 |
| **DISPLAY** | X11 display | :0 |
| **TERM** | Terminal type | xterm-256color |
| **PWD** | Current working directory | /home/user/projects |
| **PYTHONPATH** | Python module path | /opt/python/lib |
| **JAVA_HOME** | Java installation | /usr/lib/jvm/java-17 |
| Custom vars | App-specific settings | APP_CONFIG=/etc/app.conf |

### Format Details
- **Null bytes** separate key=value pairs
- Final newline
- Inherits from parent process at startup
- Modifications after process start **not** reflected here
- Some processes may restrict access (security sandboxes)

### Human-Readable Meaning
**What the process "knows" about its environment:**
- File paths it searches
- System configuration it uses
- Locale and language settings
- Custom app configuration often passed this way
- Useful for understanding why a process behaves a certain way

### Example
```
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/user
USER=user
SHELL=/bin/bash
LANG=en_US.UTF-8
DISPLAY=:0
PYTHONPATH=/opt/ml/lib
CUDA_VISIBLE_DEVICES=0,1
```
**Interpretation:**
- Standard Linux environment
- X11 display enabled (GUI capable)
- Python libraries added to path
- GPU devices 0 and 1 available to process

### Renderer Use Case
**Environment Inspector Panel:** Parse null-separated vars, display as filterable table or searchable key-value view

---

## 6. **cwd** (Symlink)
### Purpose
Link to the process's current working directory.

### Format
Symlink target:
```
/home/mrkus/Work/personal/projects/pview
```

### Key Information
| Component | Meaning | Example |
|-----------|---------|---------|
| **Target** | Actual directory path | /home/user/projects/myapp |
| **Broken link** | Process cwd deleted after startup | (symlink target disappears) |

### Format Details
- Always a symlink
- May be broken if directory was deleted
- Use `readlink()` or `realpath()` to get target
- Some processes may restrict access (permission denied)

### Human-Readable Meaning
**Where the process is "working" right now:**
- Default directory for relative file paths
- Where file output goes by default
- Useful for tracking if a process is in the right directory

### Example
```
readlink /proc/1234/cwd → /home/user/projects/webapp
```
**Interpretation:**
- Process 1234 is currently in /home/user/projects/webapp
- Any relative paths resolve from here

### Renderer Use Case
**Quick Info Display:** Show cwd in process details tooltip; warn if link is broken (directory deleted)

---

## 7. **exe** (Symlink)
### Purpose
Link to the executable that started the process.

### Format
Symlink target:
```
/usr/bin/python3
```

### Key Information
| Component | Meaning | Example |
|-----------|---------|---------|
| **Target** | Absolute path to executable | /usr/bin/python3.11 |
| **Broken link** | Executable was deleted | (symlink target disappears) |
| **Permission denied** | Restricted by security policy | (access denied) |

### Format Details
- Always a symlink
- May be broken if executable was deleted (rare)
- Real path resolves symlinks in /usr/bin -> /etc/alternatives
- May be "(deleted)" if binary was overwritten after process started
- Access may be restricted by LSM (AppArmor, SELinux)

### Human-Readable Meaning
**The exact binary that's running:**
- Resolves symlink chains (e.g., /usr/bin/python → /usr/bin/python3.11)
- Distinguishes between python vs python3 vs python3.11
- Shows if a deleted binary is still running (update needed?)
- Used for file selection dialogs, permission checks

### Example
```
readlink /proc/1234/exe → /usr/bin/python3.11 (but the symlink is /usr/bin/python3)
```
**Interpretation:**
- Process 1234 is /usr/bin/python3, which points to /usr/bin/python3.11
- Python 3.11 is what's actually running

### Renderer Use Case
**Icon & Type Detection:** Use exe path to determine process icon/category (python, java, bash, etc.)

---

## 8. **root** (Symlink)
### Purpose
Link to the process's root directory (usually /, but different in containers/chroots).

### Format
Symlink target:
```
/
```
or in containers:
```
/var/lib/docker/containers/abc123.../rootfs
```

### Key Information
| Component | Meaning | Example |
|-----------|---------|---------|
| **Target** | Root directory for this process | / or container rootfs |
| **Non-root** | Process in container/chroot/namespace | /var/lib/docker/.../rootfs |

### Format Details
- Always a symlink
- Usually points to `/` (normal process)
- Different in containers, VMs, chroots
- Indicates isolation level

### Human-Readable Meaning
**What this process thinks is the "root" of the filesystem:**
- Normal processes: /
- Containerized processes: container's root
- Indicates if process is isolated/sandboxed
- Used for security analysis

### Example
```
readlink /proc/1234/root → /
```
**Interpretation:**
- Normal system process, sees full filesystem as root

```
readlink /proc/5678/root → /var/lib/docker/containers/abc.../rootfs
```
**Interpretation:**
- Docker container, sees only container filesystem as root

### Renderer Use Case
**Container Detection:** If root != /, display container indicator; show container ID or path

---

## 9. **maps** (Regular File)
### Purpose
Virtual memory mappings - what memory ranges map to what (files, heap, stack, libraries).

### Format
Multiple lines, one mapping per line:
```
address               perms offset  dev   inode pathname
55b6fd3a0000-55b6fd3a7000 r--p 00000000 08:01 1234567 /usr/bin/python3
55b6fd3a7000-55b6fdd24000 r-xp 00007000 08:01 1234567 /usr/bin/python3
55b6fdd24000-55b6fdf16000 r--p 00183000 08:01 1234567 /usr/bin/python3
55b6fdf16000-55b6fdf17000 r--p 00374000 08:01 1234567 /usr/bin/python3
55b6fdf17000-55b6fdf19000 rw-p 00375000 08:01 1234567 /usr/bin/python3
55b6fdf19000-55b6fdf42000 rw-p 00000000 00:00 0      [heap]
7fdf5e5d9000-7fdf5e5f9000 r--p 00000000 08:01 2345678 /lib64/libc.so.6
7fdf5e5f9000-7fdf5e78b000 r-xp 00020000 08:01 2345678 /lib64/libc.so.6
7fdf5e78b000-7fdf5e7df000 r--p 001b2000 08:01 2345678 /lib64/libc.so.6
7fdf5e7df000-7fdf5e7e3000 r--p 00205000 08:01 2345678 /lib64/libc.so.6
7fdf5e7e3000-7fdf5e7e5000 rw-p 00209000 08:01 2345678 /lib64/libc.so.6
7fdf5e7e5000-7fdf5e80c000 rw-p 00000000 00:00 0      
7fdf5e923000-7fdf5e925000 rw-p 00000000 00:00 0      
7fdf5e925000-7fdf5e93a000 r--p 00000000 08:01 3456789 /lib64/ld-linux-x86-64.so.2
7fdf5e93a000-7fdf5e964000 r-xp 00015000 08:01 3456789 /lib64/ld-linux-x86-64.so.2
7fdf5e964000-7fdf5e96e000 r--p 0003f000 08:01 3456789 /lib64/ld-linux-x86-64.so.2
7fdf5e96e000-7fdf5e970000 rw-p 00049000 08:01 3456789 /lib64/ld-linux-x86-64.so.2
7fff55d3c000-7fff55d5e000 rw-p 00000000 00:00 0      [stack]
7fff55d7e000-7fff55d80000 r--p 00000000 00:00 0      [vvar]
7fff55d80000-7fff55d82000 r-xp 00000000 00:00 0      [vdso]
ffffffffff600000-ffffffffff601000 --xp 00000000 00:00 0 [vsyscall]
```

### Key Fields
| Field | Meaning | Example |
|-------|---------|---------|
| **address** | Memory range (start-end) | 55b6fd3a0000-55b6fd3a7000 |
| **perms** | Read/Write/Execute permissions | r--p (read-only), rwxp (all) |
| **offset** | Offset in file (0 for anon) | 00000000 or 00007000 |
| **dev** | Device (major:minor) | 08:01 (disk) or 00:00 (anon) |
| **inode** | File inode number | 1234567 or 0 (anonymous) |
| **pathname** | File path or special name | /usr/lib/libc.so.6, [heap], [stack], etc. |

### Mapping Types
| Pathname | Meaning | Purpose |
|----------|---------|---------|
| `/path/to/file` | File-backed mapping | Libraries, shared objects, mmap'd files |
| `[heap]` | Heap memory | malloc/new allocations |
| `[stack]` | Stack memory | Local variables, function frames |
| `[vdso]` | Virtual dynamic shared object | Kernel syscall entry points |
| `[vvar]` | Virtual variable | Kernel data (time, random, etc.) |
| `[vsyscall]` | Virtual syscall | Legacy syscall interface |
| (blank) | Anonymous memory | Untagged malloc, mmap'd anonymous regions |

### Format Details
- Address ranges in **hexadecimal**
- Size = end - start (e.g., 0x7000 = 28 KB)
- **r/w/x/p/s flags:** r=readable, w=writable, x=executable, p=private, s=shared
- **dev 00:00** = anonymous (not file-backed)
- **inode 0** = anonymous
- Lines can be very long if many mappings

### Human-Readable Meaning
**Memory layout of the process:**
- Where libraries are loaded
- Where heap/stack are located
- Which parts are writable (security concern!)
- Which files are mapped into memory
- Total addressable memory = sum of all ranges (though paging complicates this)

### Example
```
55b6fd3a0000-55b6fd3a7000 r--p 00000000 08:01 1234567 /usr/bin/python3
```
**Interpretation:**
- 28 KB read-only page
- Offset 0x0 in /usr/bin/python3
- Text segment (code)

```
55b6fdf19000-55b6fdf42000 rw-p 00000000 00:00 0 [heap]
```
**Interpretation:**
- 172 KB heap memory
- Anonymous (00:00, inode 0)
- Writable
- Contains malloc'd data

### Renderer Use Case
**Memory Layout Visualization:** Draw bars showing library, heap, stack positions; highlight RWX permissions; click to show file/type details

---

## 10. **smaps** (Regular File)
### Purpose
Detailed memory map statistics with per-mapping breakdowns of shared vs private memory.

### Format
Multiple blocks, one per mapping:
```
55b6fd3a0000-55b6fd3a7000 r--p 00000000 08:01 1234567  /usr/bin/python3
Size:                 28 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
Rss:                  28 kB
Pss:                  1 kB
Shared_Clean:         20 kB
Shared_Dirty:         0 kB
Private_Clean:        8 kB
Private_Dirty:        0 kB
Referenced:           28 kB
Anonymous:            0 kB
LazyFree:             0 kB
AnonHugePages:        0 kB
ShmemPmdMapped:       0 kB
FilePmdMapped:        0 kB
Shared_Hugetlb:       0 kB
Private_Hugetlb:      0 kB
Swap:                 0 kB
SwapPss:              0 kB
Locked:               0 kB
THPeligible:          0
VmFlags: rd mr mw me dw ac sd
```

### Key Fields to Extract
| Field | Meaning | Example |
|-------|---------|---------|
| **Size** | Virtual size of mapping (kB) | 28 |
| **Rss** | Resident set size (actual pages in RAM, kB) | 28 |
| **Pss** | Proportional set size (shared divided by # of sharers, kB) | 1 |
| **Shared_Clean** | Unmodified shared pages (kB) | 20 |
| **Shared_Dirty** | Modified shared pages (kB) | 0 |
| **Private_Clean** | Unmodified private pages (kB) | 8 |
| **Private_Dirty** | Modified private pages (kB) | 0 |
| **Referenced** | Pages recently accessed (kB) | 28 |
| **Anonymous** | Memory not backed by file (kB) | 0 |
| **Swap** | Memory swapped to disk (kB) | 0 |
| **Locked** | Pinned in RAM (mlock, kB) | 0 |
| **VmFlags** | Memory flags (rd=readable, wr=writable, etc.) | rd mr mw me dw ac sd |

### Memory Accounting Rules
- **RSS** = Shared_Clean + Shared_Dirty + Private_Clean + Private_Dirty
- **PSS** = RSS but shared pages counted as 1/N (where N = # of processes sharing)
- **Actual RAM** ≈ sum of Private + (Shared / # sharers)
- **VSZ** (virtual) doesn't mean it's in memory

### VmFlags Meanings
| Flag | Meaning |
|------|---------|
| **rd** | Readable |
| **wr** | Writable |
| **ex** | Executable |
| **sh** | Shared |
| **mr** | Mergeable |
| **mw** | May write (CoW candidate) |
| **me** | Memory error |
| **ms** | Soft dirty |
| **dw** | Do not write |
| **sd** | Stack (grows down) |
| **ac** | Arch specific |
| **ar** | Architecture reserved |
| **dd** | Data depends |
| **de** | Do not expand |

### Human-Readable Meaning
**Fine-grained memory accounting:**
- Shows exactly how much memory is shared vs private
- PSS gives more accurate memory usage than RSS
- Private pages = process's exclusive memory footprint
- Shared pages = saved by sharing (libraries loaded once)
- Referenced flag shows recently used pages

### Example
```
55b6fd3a0000-55b6fd3a7000 r--p 00000000 08:01 1234567  /usr/bin/python3
Size:                 28 kB
Rss:                  28 kB
Pss:                  1 kB
Shared_Clean:         20 kB
Private_Clean:        8 kB
```
**Interpretation:**
- Mapping is 28 kB virtual, all in RAM
- 20 kB is shared with other processes
- 8 kB is this process's exclusive copy
- True cost to system = 1 kB (shared divided by # sharers)

### Renderer Use Case
**Detailed Memory Inspector:** Show per-mapping breakdown; graph shared vs private; calculate true memory cost; highlight high-RSI (RSS/Size ratio = wasted memory)

---

## 11. **numa_maps** (Regular File)
### Purpose
NUMA (Non-Uniform Memory Access) memory distribution across nodes.

### Format
One line per mapping:
```
address pages size resident file mapped mapped-file mapmax N0=10 N1=5 kernelpagesize=4
```

### Key Fields
| Field | Meaning | Example |
|-------|---------|---------|
| **address** | Memory range | 55b6fd3a0000 |
| **pages** | Number of pages | 7 |
| **size** | Size in kB | 28 |
| **resident** | Resident pages in this node | 28 |
| **file/anon** | File-backed or anonymous | file |
| **Nx** | Pages in NUMA node x | N0=10 N1=5 |
| **kernelpagesize** | Page size (kB) | 4 |

### Format Details
- Only present on NUMA systems (most servers)
- Shows memory locality
- Ns indicate which NUMA nodes contain pages
- Useful for performance tuning on multi-socket systems

### Human-Readable Meaning
**Memory locality on multi-socket systems:**
- Shows if memory is local to CPU (fast) or remote (slow)
- Helps diagnose NUMA imbalance issues
- Remote access has higher latency

### Example
```
55b6fd3a0000 7 28 28 file /usr/bin/python3 mapped 1 N0=7 N1=0 kernelpagesize=4
```
**Interpretation:**
- 28 kB mapping all on NUMA node 0 (local/fast)

### Renderer Use Case
**Advanced: NUMA Distribution Graph** (if system has multiple NUMA nodes) - show memory distribution by node

---

## 12. **limits** (Regular File)
### Purpose
Resource limits for this process (max open files, stack size, core dumps, etc.).

### Format
Key-value pairs:
```
Limit                     Soft Limit           Hard Limit           Units     
Max cpu time              unlimited            unlimited            seconds   
Max file size             unlimited            unlimited            bytes     
Max data size             unlimited            unlimited            bytes     
Max stack size             8388608              unlimited            bytes     
Max core file size        0                    unlimited            bytes     
Max resident set          unlimited            unlimited            bytes     
Max processes             127657               127657               processes 
Max open files            65535                65535                files     
Max locked memory         65536                65536                bytes     
Max address space         unlimited            unlimited            bytes     
Max file locks            unlimited            unlimited            locks     
Max pending signals       127657               127657               signals   
Max msgqueue size         819200               819200               bytes     
Max nice priority         0                    0                    
Max realtime priority     0                    0                    
Max realtime timeout      unlimited            unlimited            us        
```

### Key Fields to Extract
| Limit | Meaning | Example |
|-------|---------|---------|
| **Max cpu time** | Cumulative CPU time | unlimited |
| **Max file size** | Max file size can write | unlimited |
| **Max data size** | Max heap size | unlimited |
| **Max stack size** | Stack size limit | 8 MB |
| **Max core file size** | Core dump size limit | 0 (disabled) |
| **Max processes** | Max threads/processes | 127657 |
| **Max open files** | File descriptor limit | 65535 |
| **Max locked memory** | mlock() limit | 64 KB |
| **Max address space** | Total virtual memory | unlimited |

### Format Details
- **Soft limit** = current limit (can be raised up to hard limit)
- **Hard limit** = absolute ceiling (can only be lowered)
- **unlimited** = no restriction
- Units vary (seconds, bytes, etc.)

### Human-Readable Meaning
**Resource constraints on the process:**
- File descriptor limit explains "too many open files" errors
- Stack size affects deep recursion
- Core file size determines crash dump capture
- Process limit caps spawning of child processes
- CPU time limit kills runaway processes

### Example
```
Max cpu time              unlimited            unlimited            seconds   
Max open files            65535                65535                files     
Max processes             127657               127657               processes 
Max stack size             8388608              unlimited            bytes     
```
**Interpretation:**
- Can open up to 65535 files
- Can create up to 127657 processes
- Stack is limited to 8 MB
- No CPU time limit (unlimited)

### Renderer Use Case
**Limits Inspector Panel:** Show all limits; highlight constraints; warn if stack/core dump are suspiciously low

---

## 13. **io** (Regular File)
### Purpose
I/O statistics - bytes/operations read and written.

### Format
Key-value pairs:
```
rchar: 1234567
wchar: 7654321
syscr: 12345
syscw: 6789
read_bytes: 2097152
write_bytes: 4194304
cancelled_write_bytes: 0
```

### Key Fields
| Field | Meaning | Example |
|-------|---------|---------|
| **rchar** | Characters read from filesystem (bytes) | 1234567 |
| **wchar** | Characters written to filesystem (bytes) | 7654321 |
| **syscr** | Number of read syscalls | 12345 |
| **syscw** | Number of write syscalls | 6789 |
| **read_bytes** | Actual disk bytes read | 2097152 (2 MB) |
| **write_bytes** | Actual disk bytes written | 4194304 (4 MB) |
| **cancelled_write_bytes** | Writes cancelled (page reclaim) | 0 |

### Format Details
- **rchar/wchar** = application-level I/O (system calls)
- **read_bytes/write_bytes** = actual disk I/O (includes cache)
- rchar can be > read_bytes (disk cache hits)
- syscr/syscw = number of calls, not individual byte counts

### Human-Readable Meaning
**How much disk I/O this process has done:**
- High read/write suggests disk-intensive workload
- Ratio of syscalls to bytes shows call efficiency
- read_bytes vs rchar shows cache effectiveness
- Useful for I/O profiling and bottleneck detection

### Example
```
rchar: 1000000
read_bytes: 100000
```
**Interpretation:**
- 1 MB requested by application
- Only 100 KB actually read from disk (90% cache hits!)

### Renderer Use Case
**I/O Stats Panel:** Show read/write rates; highlight disk-intensive processes; graph I/O over time

---

## 14. **mountinfo** (Regular File)
### Purpose
Mount points and filesystems accessible to this process (affected by mount namespaces).

### Format
Multiple lines, one mount per line:
```
ID PARENT_ID MAJOR:MINOR ROOT SUB_MOUNTS MOUNT_POINT MOUNT_OPTIONS ... FILESYSTEM_TYPE MOUNT_SOURCE SUPER_OPTIONS
23 1 8:1 / / / rw,relatime shared:1 - ext4 /dev/sda1 rw
24 23 0:3 / / /proc rw,nosuid,nodev,noexec,relatime shared:2 - proc proc rw
25 23 0:4 / / /sys rw,nosuid,nodev,noexec,relatime shared:3 - sysfs sysfs rw
26 23 0:5 / / /dev rw,nosuid,size=3958288k,mode=755,inode64 shared:4 - devtmpfs devtmpfs rw,size=3958288k,mode=755,inode64
27 26 0:6 / / /dev/shm rw,nosuid,nodev shared:5 - tmpfs tmpfs rw,nosuid,nodev
28 23 0:7 / / /run rw,nosuid,nodev,relatime shared:6 - tmpfs tmpfs rw,nosuid,nodev,relatime,size=1582632k,mode=755
29 23 8:2 / / /boot rw,relatime shared:7 - ext4 /dev/sda2 rw
30 29 8:2 / /efi /boot/efi rw,relatime shared:8 - vfat /dev/sda3 rw
31 23 10:0 / / /mnt/nfs rw,relatime shared:9 - nfs 192.168.1.100:/export rw
```

### Key Fields
| Field | Meaning | Example |
|-------|---------|---------|
| **ID** | Unique mount ID | 23 |
| **PARENT_ID** | Parent mount ID | 1 |
| **MAJOR:MINOR** | Device numbers | 8:1 |
| **ROOT** | Root of mounted filesystem | / |
| **MOUNT_POINT** | Where mounted | /proc |
| **MOUNT_OPTIONS** | How mounted (rw, ro, etc.) | rw,relatime |
| **FILESYSTEM_TYPE** | FS type | ext4, proc, sysfs, tmpfs |
| **MOUNT_SOURCE** | Device or location | /dev/sda1, proc, tmpfs |

### Important Options
| Option | Meaning |
|--------|---------|
| **rw** | Read-write |
| **ro** | Read-only |
| **nosuid** | SUID bits ignored |
| **nodev** | Device files not allowed |
| **noexec** | Executables can't run |
| **shared** | Mounts shared between namespaces |
| **private** | Mounts isolated |
| **slave** | Receives propagation |
| **unbindable** | Can't be bound elsewhere |

### Human-Readable Meaning
**What filesystems this process can access:**
- Root process sees all mounts
- Containerized process has restricted view
- Indicates what is read-only vs writable
- Shows mount isolation (container security)

### Example
```
23 1 8:1 / / / rw,relatime shared:1 - ext4 /dev/sda1 rw
```
**Interpretation:**
- Main filesystem /dev/sda1 mounted at / as ext4, read-write

```
26 23 0:5 / / /dev rw,nosuid,size=3958288k,mode=755,inode64 shared:4 - devtmpfs devtmpfs rw
```
**Interpretation:**
- /dev mounted as devtmpfs (not a real block device)
- nosuid means setuid programs won't work on this mount
- Shared means all processes see same /dev

### Renderer Use Case
**Filesystem View:** Show mounted filesystems; indicate read-only vs RW; highlight container-specific mounts; show mount options/restrictions

---

## 15. **ns/** (Directory with Symlinks)
### Purpose
Namespace links - shows what namespaces this process belongs to.

### Format
Multiple symlinks, each pointing to a namespace inode:
```
cgroup -> cgroup:[4026531835]
ipc -> ipc:[4026531839]
mnt -> mnt:[4026531840]
net -> net:[4026531956]
pid -> pid:[4026531836]
pid_for_children -> pid:[4026531836]
time -> time:[4026531834]
time_for_children -> time:[4026531834]
user -> user:[4026531837]
uts -> uts:[4026531838]
```

### Namespace Types
| Type | Meaning | Isolation | Example |
|------|---------|-----------|---------|
| **pid** | Process namespace | Process tree, signals | Containers see different PID 1 |
| **net** | Network namespace | Network stack, interfaces | Container has own localhost, routes |
| **mnt** | Mount namespace | Filesystem mounts | Container sees different /proc, /sys |
| **ipc** | IPC namespace | Message queues, semaphores | Processes in different IPC can't share |
| **uts** | UTS namespace | Hostname, domainname | Containers have different hostnames |
| **user** | User namespace | UID/GID mappings | Containers have root (UID 0) but not real |
| **cgroup** | Cgroup namespace | Cgroup hierarchy | Container sees isolated cgroup view |
| **time** | Time namespace | CLOCK_MONOTONIC, CLOCK_BOOTTIME | Container can have different "boot time" |

### Format Details
- Value in brackets = inode number (same inode = shared namespace)
- Processes with same inode share that namespace type
- Symlink targets are not resolvable (special kernel structures)

### Human-Readable Meaning
**Isolation level of the process:**
- Root process has main namespaces (e.g., pid:[4026531836])
- Containerized processes have different namespace inodes
- Shared inodes = processes in same container/group
- Shows security/isolation boundaries

### Example
```
readlink /proc/1/ns/pid → pid:[4026531836]
readlink /proc/1234/ns/pid → pid:[4026531836]
readlink /proc/5678/ns/pid → pid:[4026532247]
```
**Interpretation:**
- Processes 1 and 1234 share PID namespace (same system)
- Process 5678 is in different container (different PID namespace inode)

### Renderer Use Case
**Container Detection & Grouping:** Compare namespace inodes to detect containers; group processes by shared namespaces

---

## 16. **fd/** (Directory with Symlinks)
### Purpose
File descriptors - symlinks to all open files/sockets/pipes for this process.

### Format
Multiple numeric symlinks:
```
0 -> /dev/pts/0
1 -> /dev/pts/0
2 -> /dev/pts/0
3 -> socket:[3456789]
4 -> /home/user/data.txt
5 -> pipe:[3456790]
6 -> /proc/1234/fd
7 -> anon_inode:[eventpoll]
8 -> /var/log/app.log (deleted)
```

### File Descriptor Types
| Type | Meaning | Example |
|------|---------|---------|
| **Regular file** | Normal file | /home/user/data.txt |
| **Directory** | Open directory | /home/user |
| **Device** | Character/block device | /dev/pts/0 (terminal) |
| **socket** | Network socket | socket:[3456789] |
| **pipe** | Pipe | pipe:[3456790] |
| **anon_inode** | Kernel structure | [eventpoll], [timerfd] |
| **(deleted)** | Deleted but still open | /home/user/temp.txt (deleted) |

### Special File Descriptors
| FD | Meaning | Example |
|----|---------|---------|
| **0** | stdin | /dev/pts/0 |
| **1** | stdout | /dev/pts/0 or /var/log/app.log |
| **2** | stderr | /dev/pts/0 |
| **3+** | Application-opened files | Database connections, config files, sockets |

### Format Details
- Numeric names = file descriptor numbers
- Symlink target shows what's open
- **(deleted)** suffix = file was unlinked but still open (monitoring cleanup)
- Can't resolve some symlinks (permission denied)

### Human-Readable Meaning
**All files/sockets this process has open:**
- Shows what files process is accessing
- Detects file descriptor leaks (FDs not closed)
- Shows network connections (socket inodes)
- Detects zombie files (deleted but still open)
- Explains "too many open files" errors

### Example
```
0 -> /dev/pts/0        (stdin from terminal)
1 -> /var/log/app.log  (stdout redirected to log)
2 -> /var/log/app.log  (stderr redirected to log)
3 -> socket:[3456789]  (network connection)
4 -> /home/user/data.db (database file)
5 -> pipe:[3456790]    (pipe to child process)
8 -> /home/user/temp.txt (deleted)
```
**Interpretation:**
- Process is running with stdio redirected to /var/log/app.log
- Has 1 network connection (socket)
- Has database open
- Has deleted temp file still open (should be cleaned up)

### Renderer Use Case
**File Descriptor Inspector:** Show open files as sortable table; highlight sockets/pipes/special types; warn about deleted files; show file counts

---

## 17. **task/** (Directory with subdirectories)
### Purpose
Individual threads in this process. Each subdirectory is a thread with its own /proc/[pid]/task/[tid]/ layout.

### Format
Multiple numeric directories:
```
task/
├── 1234/
│   ├── stat
│   ├── status
│   ├── comm
│   └── ... (same structure as /proc/[pid]/)
├── 1235/
│   ├── stat
│   ├── status
│   ├── comm
│   └── ...
└── 1236/
    ├── stat
    ├── status
    ├── comm
    └── ...
```

### Key Information
| File | Meaning | Example |
|------|---------|---------|
| **Number** | Thread ID (TID) | 1234, 1235, 1236 |
| **stat** | Per-thread scheduling stats | Like /proc/[pid]/stat for this thread |
| **comm** | Per-thread name | Worker-1, Worker-2 (can differ from process name) |
| **status** | Per-thread status | Per-thread resource info |

### Format Details
- Each TID has own /proc/[pid]/task/[tid]/ directory
- TID 1234 is the main thread (same as PID)
- Files mirror parent /proc/[pid]/ structure
- Stat data shows per-thread CPU usage

### Human-Readable Meaning
**Individual threads within the process:**
- Each thread has own stats
- Can track CPU usage per thread
- Can see thread names (if set)
- Shows which threads are busy vs idle

### Example
```
task/
├── 1234/ (main thread)
│   stat: ... 1234 (python) S ... utime=234 stime=56 ...
├── 1235/ (worker thread)
│   stat: ... 1235 (python) R ... utime=900 stime=10 ...
└── 1236/ (I/O thread)
    stat: ... 1236 (python) S ... utime=10 stime=234 ...
```
**Interpretation:**
- Main thread (1234): sleeping
- Worker thread (1235): running, high CPU (900 jiffies user time)
- I/O thread (1236): sleeping, mostly in kernel (234 jiffies stime)

### Renderer Use Case
**Thread Inspector:** List all threads; show per-thread CPU usage; highlight busy threads; allow filtering/sorting by state/CPU

---

## 18. **sched** (Regular File)
### Purpose
Scheduler information - CPU time, context switches, wait time on runqueue.

### Format
Scheduler stats (kernel version dependent):
```
se.exec_start                                :      12345678
se.vruntime                                  :      987654
se.sum_exec_runtime                          :      567890
se.nr_migrations                             :          45
nr_switches                                  :       12345
nr_forced_migrations                         :          10
nr_wakeups                                   :        9876
nr_wakeups_sync                              :           0
nr_wakeups_migrate                           :          12
nr_wakeups_local                             :        9864
nr_wakeups_remote                            :          12
nr_wakeups_affine                            :           0
nr_wakeups_affine_attempts                   :           0
nr_wakeups_passive                           :           0
nr_wakeups_idle                              :           0
```

### Key Fields to Extract
| Field | Meaning | Example |
|-------|---------|---------|
| **se.exec_start** | When started current execution | 12345678 |
| **se.vruntime** | Virtual runtime (scheduler time) | 987654 |
| **se.sum_exec_runtime** | Total execution time (nanoseconds) | 567890 |
| **se.nr_migrations** | Times moved between CPUs | 45 |
| **nr_switches** | Total context switches | 12345 |
| **nr_forced_migrations** | Forced CPU migrations | 10 |
| **nr_wakeups** | Number of wakeups | 9876 |
| **nr_wakeups_sync** | Synchronous wakeups | 0 |
| **nr_wakeups_migrate** | Wakeups requiring CPU migration | 12 |

### Format Details
- Times in **nanoseconds** (convert to ms/s by dividing by 1,000,000 or 1,000,000,000)
- **vruntime** = fair scheduler's virtual time (higher = less deserving)
- **nr_switches** = context switches (high = frequently preempted)
- **nr_migrations** = CPU migrations (high = load balancing / cache misses)

### Human-Readable Meaning
**Scheduler behavior and fairness:**
- Low vruntime = process gets more CPU (deserving)
- High context switches = frequently preempted (competing workload)
- Migrations indicate load balancing or CPU affinity issues
- Shows scheduler "fairness" perception

### Example
```
se.sum_exec_runtime                          :      567890000
nr_switches                                  :       12345
nr_forced_migrations                         :          10
```
**Interpretation:**
- ~568 milliseconds of CPU time used
- Context switched 12345 times
- Forced to migrate CPUs 10 times

### Renderer Use Case
**Scheduler Inspector:** Show execution time, context switches, migrations; highlight high-migration processes; gauge fairness

---

## 19. **oom_score** (Regular File)
### Purpose
Out-of-Memory (OOM) killer badness score - likelihood of being killed when memory runs out.

### Format
Single integer (0-1000):
```
823
```

### Key Information
| Value | Meaning |
|-------|---------|
| **0-100** | Low priority (unlikely to be killed) |
| **100-500** | Medium priority |
| **500-800** | High priority (likely killed first) |
| **800+** | Very high priority (killed early) |
| **0** | Privileged process (system critical) |

### Scoring Formula
```
badness = (memory_used * 1000 / total_memory) + oom_score_adj
```

### Format Details
- Kernel calculates score based on memory consumption
- Can be manually adjusted via `oom_score_adj` in status file
- System processes often have 0 or negative scores
- Memory hogs get highest scores

### Human-Readable Meaning
**Which processes will be killed first if system runs out of memory:**
- High score = first to die
- Low score = protected
- System critical (init, kernel threads) have 0

### Example
```
823
```
**Interpretation:**
- Very high OOM score
- This process will likely be killed first if memory exhausted

### Renderer Use Case
**OOM Indicator:** Show score; highlight processes with high scores (memory hogs); warn if high on system with low free memory

---

## 20. **attr/** (Directory)
### Purpose
SELinux security attributes (if SELinux enabled).

### Format
Multiple files representing security context:
```
attr/
├── current
├── exec
├── fscreate
├── keycreate
├── prev
├── sockcreate
└── display
```

### Key Files
| File | Meaning | Example |
|------|---------|---------|
| **current** | Current SELinux context | system_u:system_r:init_t:s0 |
| **exec** | Context for next execve() | system_u:system_r:init_t:s0 |
| **fscreate** | Context for new files | system_u:system_r:init_t:s0 |
| **sockcreate** | Context for new sockets | system_u:system_r:init_t:s0 |
| **prev** | Previous context | (empty or previous) |

### SELinux Context Format
```
user_identity:role:type:sensitivity[:category]
```

| Component | Meaning | Example |
|-----------|---------|---------|
| **user_identity** | SELinux user | system_u, unconfined_u |
| **role** | Role | system_r, unconfined_r |
| **type** | Type (security policy) | init_t, httpd_t |
| **sensitivity** | Classification level | s0, s0:c0 |

### Format Details
- Only present if SELinux enabled
- Files may not exist on systems without SELinux
- Reading may be restricted by policy

### Human-Readable Meaning
**SELinux security classification:**
- Type determines what the process can access
- Role determines capabilities
- Shows if process is confined or unconfined

### Example
```
system_u:system_r:init_t:s0
```
**Interpretation:**
- System user, system role, init type
- Privileged initialization process

```
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```
**Interpretation:**
- User process, unconfined type
- Full access (not restricted by SELinux)

### Renderer Use Case
**Security Info Panel:** Show SELinux context if available; highlight unconfined processes; warn about confinement issues

---

## 21. **coredump_filter** (Regular File)
### Purpose
Bitmask controlling what gets included in core dumps.

### Format
Hexadecimal bitmask:
```
33
```

### Bit Meanings
| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | 1 (0x01) | Anonymous memory (heap, stack) |
| 1 | 2 (0x02) | File-backed memory (mmapped files) |
| 2 | 4 (0x04) | Shared memory (shmem) |
| 3 | 8 (0x08) | ELF header |
| 4 | 16 (0x10) | Private huge pages |
| 5 | 32 (0x20) | Shared huge pages |
| 6 | 64 (0x40) | Private DAX pages |
| 7 | 128 (0x80) | Shared DAX pages |

### Format Details
- Hexadecimal value
- Typical value: 0x33 (binary: 00110011)
  - Includes: anonymous (1), file-backed (2), shared (32) = 1+2+32 = 35 = 0x23 (or with defaults)
- Each bit toggles whether that memory type is included in core dump

### Human-Readable Meaning
**What's saved when process crashes:**
- Heap/stack usually included
- Large files or sensitive data might be excluded
- Affects core dump size and time to save

### Example
```
33 (hex) = 51 (decimal) = binary 110011
```
**Interpretation:**
- Bits 0,1,4,5 set
- Includes: anonymous, file-backed, private huge pages, shared huge pages
- Does NOT include: shared memory, ELF header, DAX pages

### Renderer Use Case
**Debug Info Panel:** Show coredump filter settings; explain what will be in crash dumps

---

## 22. **latency** (Regular File - if CONFIG_LATENCY_HIST enabled)
### Purpose
Histogram of scheduler latency (if kernel compiled with latency tracking).

### Format
Distribution of task wakeup latencies:
```
Latency histogram (nanoseconds):
    0-1 us   : 123
    1-2 us   : 456
    2-4 us   : 789
    4-8 us   : 234
    8-16 us  : 567
   16-32 us  : 89
   32-64 us  : 12
  64-128 us : 3
  128-256 us: 1
  256-512 us: 0
    >512 us : 0
```

### Format Details
- Not available on most systems (kernel config dependent)
- Shows response time distribution
- Useful for real-time analysis

### Human-Readable Meaning
**How quickly the scheduler responds to wakeups:**
- Low latencies = responsive system
- High latencies = busy or misconfigured

### Renderer Use Case
**Performance Analysis (Advanced):** Graph latency distribution if available

---

## Summary Table

| File | Type | Purpose | Key Use |
|------|------|---------|---------|
| stat | File | Scheduling statistics | CPU usage, process state, page faults |
| statm | File | Memory in pages | Quick RSS/VSZ |
| status | File | Human-readable status | All detailed info (preferred format) |
| cmdline | File | Command line | Show how process started |
| environ | File | Environment variables | Debug env issues |
| cwd | Symlink | Current directory | Where process is working |
| exe | Symlink | Executable path | Determine process type |
| root | Symlink | Process root | Detect containers |
| maps | File | Memory layout | Visualize address space |
| smaps | File | Detailed memory stats | Accurate memory accounting |
| numa_maps | File | NUMA distribution | Multi-socket servers only |
| limits | File | Resource limits | Show constraints |
| io | File | I/O statistics | Track disk-heavy processes |
| mountinfo | File | Mount info | Filesystem access, containers |
| ns/ | Directory | Namespaces | Container detection, grouping |
| fd/ | Directory | Open files | Detect leaks, see connections |
| task/ | Directory | Threads | Per-thread stats |
| sched | File | Scheduler info | Load, fairness, migrations |
| oom_score | File | OOM priority | Prediction of crash if OOM |
| attr/ | Directory | SELinux context | Security attributes |
| coredump_filter | File | Core dump settings | Debug configuration |

---

## Renderer Implementation Strategy

### Phase 1: Core Renderers
1. **Process Summary** (stat + status)
   - State, CPU, memory, threads
   - Quick glance at process health

2. **Command & Environment**
   - cmdline and environ parsers
   - Show startup parameters and env

3. **Memory Visualization** (statm, maps, smaps)
   - Graph memory layout
   - Show shared vs private
   - Warn about memory issues

### Phase 2: Advanced Renderers
4. **File Descriptors** (fd/)
   - List open files/sockets
   - Detect fd leaks

5. **Threads** (task/)
   - Per-thread stats
   - CPU usage per thread

6. **I/O Profiling** (io/)
   - Read/write rates
   - Disk activity

### Phase 3: Security & Debugging
7. **Limits** (limits)
   - Show resource constraints
   - Explain "too many open files" etc.

8. **Security Attributes** (attr/, oom_score)
   - SELinux context
   - OOM likelihood

9. **Scheduler Info** (sched)
   - Context switches
   - CPU migrations

### Phase 4: Container & Advanced
10. **Namespace Analysis** (ns/)
    - Container detection
    - Isolation level

11. **Mount Info** (mountinfo)
    - Filesystem access
    - Read-only warnings

12. **NUMA Distribution** (numa_maps)
    - Memory locality (servers only)

