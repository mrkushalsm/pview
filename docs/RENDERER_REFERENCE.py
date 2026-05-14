#!/usr/bin/env python3
"""
Quick Reference: What Each Renderer Shows

This file demonstrates what output each renderer produces
and what /proc file it handles.

This list covers the 27 specialized renderers plus the TextRenderer fallback.
"""

renderers = {
    # Core Process Info
    "StatRenderer": {
        "file": "/proc/[pid]/stat",
        "example": "991 (pipewire) S 1 991 991 0 -1 4218880 ...",
        "output": "State: S (Sleeping), Parent PID: 1, CPU time: 2.3s user, 0.4s system, Memory: 128 MiB",
        "use_case": "Understand process CPU usage, state (running/sleeping/zombie), memory footprint"
    },
    
    "StatmRenderer": {
        "file": "/proc/[pid]/statm",
        "example": "32768 12345 5000 100 0 200 0",
        "output": "Total VM: 128 MiB, RSS: 49.4 MiB, Shared: 20 MiB, Data+Stack: 0.8 MiB",
        "use_case": "See how much memory process actually uses vs virtual allocation"
    },
    
    "StatusRenderer": {
        "file": "/proc/[pid]/status",
        "example": "Name: pipewire\nPid: 991\nState: S (sleeping)\n...",
        "output": "Formatted table: Name, PID, Parent, State, Threads, Memory, UID/GID, Security",
        "use_case": "Complete process snapshot with all important metrics in one place"
    },
    
    "CmdlineRenderer": {
        "file": "/proc/[pid]/cmdline",
        "example": "/usr/bin/python3\0-m\0pview\0--debug\0",
        "output": "Command: /usr/bin/python3\nArgs: [-m, pview, --debug]",
        "use_case": "See what arguments were passed to a running process"
    },
    
    "EnvironRenderer": {
        "file": "/proc/[pid]/environ",
        "example": "PATH=/usr/bin:/bin\0HOME=/root\0...",
        "output": "PATH=/usr/bin:/bin\nHOME=/root\nSHELL=/bin/bash\n...",
        "use_case": "Debug: what environment variables is this process seeing?"
    },
    
    # Resource Limits
    "LimitsRenderer": {
        "file": "/proc/[pid]/limits",
        "example": "Limit\t\t\tSoft Limit\tHard Limit\tUnits\nMax stack size\t8388608\t\tunlimited\tbytes",
        "output": "Max cpu time: unlimited, Max files: 1024/65536, Max stack: 8.4MB",
        "use_case": "Diagnose why a process can't open more files or allocate more memory"
    },
    
    "OomScoreRenderer": {
        "file": "/proc/[pid]/oom_score",
        "example": "234",
        "output": "Score: 234 (High kill risk) - Will be killed if system runs out of memory",
        "use_case": "Check OOM killer priority - high scores killed first"
    },
    
    "OomScoreAdjRenderer": {
        "file": "/proc/[pid]/oom_score_adj",
        "example": "-100",
        "output": "Adjustment: -100 (Low priority) - Less likely to be killed",
        "use_case": "See if process is protected from OOM killer (negative = protected)"
    },
    
    "FdRenderer": {
        "file": "/proc/[pid]/fd/",
        "example": "0 -> /dev/pts/1\n1 -> /dev/pts/1\n3 -> /var/log/app.log",
        "output": "Table: FD# | Type | Flags | Resolved Path",
        "use_case": "See what files a process has open - debug file descriptor leaks"
    },
    
    # Isolation & Security
    "NamespacesRenderer": {
        "file": "/proc/[pid]/ns/",
        "example": "ipc, mnt, net, pid, user, uts, cgroup, time symlinks",
        "output": "Table showing each namespace type and inode number (shared = same inode)",
        "use_case": "Check if process is containerized or shares namespaces with others"
    },
    
    "AttrRenderer": {
        "file": "/proc/[pid]/attr/",
        "example": "current -> user_u:role_r:user_t:s0-s0:c0.c1023",
        "output": "SELinux context: user_u:role_r:user_t (decoded)",
        "use_case": "Debug SELinux permissions - see what security context process runs under"
    },
    
    "CgroupRenderer": {
        "file": "/proc/[pid]/cgroup",
        "example": "0::/user.slice/user-1000.slice\n1:cpuset,cpu:/docker/abc123",
        "output": "Hierarchies: [0] system.slice/user-1000, [1] cpu in /docker/abc123",
        "use_case": "See resource group - is it in container? Which cgroup controllers limit it?"
    },
    
    "MountinfoRenderer": {
        "file": "/proc/[pid]/mountinfo",
        "example": "25 0 8:1 / / rw,relatime - ext4 /dev/sda1",
        "output": "Mount points: / (ext4), /dev (tmpfs), /sys (sysfs), /proc (proc)",
        "use_case": "See filesystems visible to process - important in containers/chroots"
    },
    
    # Memory Details
    "MapsRenderer": {
        "file": "/proc/[pid]/maps",
        "example": "7f1234567000-7f1234668000 r-xp 00000000 08:01 1234567 /lib64/libc.so.6",
        "output": "Memory regions with [X] [W] [R] flags and associated file",
        "use_case": "See memory layout - where is code, heap, libraries, stack?"
    },
    
    "SmapsRenderer": {
        "file": "/proc/[pid]/smaps",
        "example": "7f...-7f... r-x\nSize: 1024\nRss: 256\nPss: 128",
        "output": "Total PSS: 42 MiB (accounting for shared pages fairly)",
        "use_case": "Accurate memory usage - PSS accounts for sharing, RSS doesn't"
    },
    
    "NumaMapsRenderer": {
        "file": "/proc/[pid]/numa_maps",
        "example": "7f123000 default file=/lib64/libc.so.6 mapped=42 N0=42",
        "output": "NUMA distribution: pages on nodes N0, N1, N2, etc.",
        "use_case": "On NUMA systems, check if process memory is on local or remote nodes"
    },
    
    # Activity
    "IoRenderer": {
        "file": "/proc/[pid]/io",
        "example": "read_bytes: 1234567\nwrite_bytes: 987654",
        "output": "I/O: read 1.2GB, write 988KB, read ops: 50, write ops: 30",
        "use_case": "Profile I/O - is process doing lots of disk operations?"
    },
    
    "SchedRenderer": {
        "file": "/proc/[pid]/sched",
        "example": "pipewire (991, #threads: 1)\nse.exec_start: 123456789",
        "output": "Scheduler info: runtime, context switches, priority, wake-ups",
        "use_case": "Debug performance - how much CPU time? Context switches?"
    },

    "TaskRenderer": {
        "file": "/proc/[pid]/task/",
        "example": "991/\n992/\n993/",
        "output": "Thread list: TID, state, CPU usage, and per-thread details",
        "use_case": "Inspect all threads belonging to a process"
    },

    "NetTcpRenderer": {
        "file": "/proc/[pid]/net/tcp",
        "example": "local_address rem_address st ...",
        "output": "TCP socket table with decoded endpoints and connection state",
        "use_case": "Debug TCP connections owned by a process"
    },

    "NetUdpRenderer": {
        "file": "/proc/[pid]/net/udp",
        "example": "local_address rem_address st ...",
        "output": "UDP socket table with decoded endpoints and queue stats",
        "use_case": "Inspect UDP sockets and ports in use"
    },

    "NetUnixRenderer": {
        "file": "/proc/[pid]/net/unix",
        "example": "Num RefCount Protocol Flags Type St Inode Path",
        "output": "UNIX socket table with paths and connection metadata",
        "use_case": "Trace local IPC sockets and file-backed UNIX sockets"
    },

    "NetDevRenderer": {
        "file": "/proc/[pid]/net/dev",
        "example": "Inter-| Receive | Transmit\nface |bytes ...",
        "output": "Per-interface traffic counters with RX/TX byte and packet totals",
        "use_case": "Check per-process network interface activity"
    },

    "SymlinkRenderer": {
        "file": "/proc/[pid]/exe, /proc/[pid]/cwd, /proc/[pid]/root, /proc/[pid]/fd/*, /proc/[pid]/ns/*",
        "example": "exe -> /usr/bin/python3",
        "output": "Resolved symlink targets with path meaning and access notes",
        "use_case": "Show where proc symlinks point instead of reporting them as unavailable"
    },
    
    # System-Wide
    "MemInfoRenderer": {
        "file": "/proc/meminfo",
        "example": "MemTotal: 16384000 kB\nMemFree: 8192000 kB",
        "output": "Memory bars: MemFree 50% [████░░░░], Cached, Swap, etc.",
        "use_case": "System memory overview - how much free? How much cached?"
    },
    
    "CpuInfoRenderer": {
        "file": "/proc/cpuinfo",
        "example": "processor: 0\nmodel name: Intel Core i7\ncpu MHz: 3400.0",
        "output": "CPUs: 4 cores, 2.4GHz base, supports: AVX, SSE4.2, AES-NI",
        "use_case": "CPU info - cores, frequency, features (SSE, AVX for performance)"
    },
    
    # Advanced
    "CoredumpFilterRenderer": {
        "file": "/proc/[pid]/coredump_filter",
        "example": "0x33",
        "output": "Included in core dumps: [✓] anon, [✓] shared, [✓] text, [✓] elf",
        "use_case": "Debug: which memory regions are saved in crash dumps?"
    },
    
    # Fallback
    "TextRenderer": {
        "file": "any unmapped file",
        "example": "raw text content",
        "output": "Nicely formatted raw text with highlighting",
        "use_case": "Safety net - displays anything renderer doesn't specifically handle"
    },
}

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PVIEW RENDERER QUICK REFERENCE")
    print("="*80 + "\n")
    
    for renderer, info in renderers.items():
        print(f"🔍 {renderer}")
        print(f"   File:       {info['file']}")
        print(f"   Example:    {info['example'][:60]}...")
        print(f"   Shows:      {info['output']}")
        print(f"   Use:        {info['use_case']}")
        print()
    
    print("\n" + "="*80)
    print(f"Total: {len(renderers)} renderers")
    print("="*80 + "\n")
    
    print("📝 Tips:")
    print("  • Navigate with arrow keys in pview")
    print("  • Expand directories to see files")
    print("  • Click on any file to view formatted output")
    print("  • Each renderer shows human-readable interpretation")
    print("  • No raw hex - all conversions applied (jiffies→seconds, KiB→MiB)")
    print()
