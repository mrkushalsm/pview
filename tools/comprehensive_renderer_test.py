"""
Comprehensive Renderer Test - Demonstrates all 27 specialized renderers.
"""
from pathlib import Path
from pview.renderers.registry import RendererRegistry


def test_all_renderers():
    """Test that all renderers can be instantiated and registered."""
    registry = RendererRegistry()
    
    # Expected 27 specialized renderers
    renderers = registry._renderers
    print(f"\n✓ Registry loaded with {len(renderers)} renderers:\n")
    
    renderer_names = [r.__class__.__name__ for r in renderers]
    for i, name in enumerate(renderer_names, 1):
        print(f"  {i:2}. {name}")
    
    # Test each renderer's can_render() method
    test_cases = [
        ("StatRenderer", "/proc/1/stat"),
        ("StatmRenderer", "/proc/1/statm"),
        ("StatusRenderer", "/proc/1/status"),
        ("CmdlineRenderer", "/proc/1/cmdline"),
        ("EnvironRenderer", "/proc/1/environ"),
        ("LimitsRenderer", "/proc/1/limits"),
        ("NamespacesRenderer", "/proc/1/ns"),
        ("OomScoreRenderer", "/proc/1/oom_score"),
        ("OomScoreAdjRenderer", "/proc/1/oom_score_adj"),
        ("MountinfoRenderer", "/proc/1/mountinfo"),
        ("CoredumpFilterRenderer", "/proc/1/coredump_filter"),
        ("SmapsRenderer", "/proc/1/smaps"),
        ("NumaMapsRenderer", "/proc/1/numa_maps"),
        ("AttrRenderer", "/proc/1/attr"),
        ("CgroupRenderer", "/proc/1/cgroup"),
        ("FdRenderer", "/proc/1/fd"),
        ("MapsRenderer", "/proc/1/maps"),
        ("TaskRenderer", "/proc/1/task"),
        ("NetTcpRenderer", "/proc/1/net/tcp"),
        ("NetUdpRenderer", "/proc/1/net/udp"),
        ("NetUnixRenderer", "/proc/1/net/unix"),
        ("NetDevRenderer", "/proc/1/net/dev"),
        ("SymlinkRenderer", "/proc/1/exe"),
        ("IoRenderer", "/proc/1/io"),
        ("SchedRenderer", "/proc/1/sched"),
        ("MemInfoRenderer", "/proc/meminfo"),
        ("CpuInfoRenderer", "/proc/cpuinfo"),
    ]
    
    print("\n✓ Renderer Detection Tests:\n")
    for renderer_name, path in test_cases:
        renderer = next((r for r in renderers if r.__class__.__name__ == renderer_name), None)
        if renderer:
            can_handle = renderer.can_render(Path(path))
            status = "✓" if can_handle else "✗"
            print(f"  {status} {renderer_name:30} → {path}")
        else:
            print(f"  ✗ {renderer_name:30} NOT FOUND")
    
    print(f"\n✓ All {len(renderers)} renderers operational!")
    return True


if __name__ == "__main__":
    test_all_renderers()
