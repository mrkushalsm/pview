from pathlib import Path

from rich.panel import Panel

from pview.renderers.attr_renderer import AttrRenderer
from pview.renderers.cgroup_renderer import CgroupRenderer
from pview.renderers.cmdline_renderer import CmdlineRenderer
from pview.renderers.coredump_filter_renderer import CoredumpFilterRenderer
from pview.renderers.environ_renderer import EnvironRenderer
from pview.renderers.fd_renderer import FdRenderer
from pview.renderers.io_renderer import IoRenderer
from pview.renderers.limits_renderer import LimitsRenderer
from pview.renderers.maps_renderer import MapsRenderer
from pview.renderers.meminfo_renderer import MemInfoRenderer
from pview.renderers.mountinfo_renderer import MountinfoRenderer
from pview.renderers.net_dev_renderer import NetDevRenderer
from pview.renderers.net_tcp_renderer import NetTcpRenderer
from pview.renderers.net_udp_renderer import NetUdpRenderer
from pview.renderers.net_unix_renderer import NetUnixRenderer
from pview.renderers.namespaces_renderer import NamespacesRenderer
from pview.renderers.numa_maps_renderer import NumaMapsRenderer
from pview.renderers.oom_score_adj_renderer import OomScoreAdjRenderer
from pview.renderers.oom_score_renderer import OomScoreRenderer
from pview.renderers.registry import RendererRegistry
from pview.renderers.sched_renderer import SchedRenderer
from pview.renderers.smaps_renderer import SmapsRenderer
from pview.renderers.symlink_renderer import SymlinkRenderer
from pview.renderers.stat_renderer import StatRenderer
from pview.renderers.statm_renderer import StatmRenderer
from pview.renderers.status_renderer import StatusRenderer
from pview.renderers.task_renderer import TaskRenderer
from pview.renderers.text_renderer import TextRenderer
from pview.renderers.cpuinfo_renderer import CpuInfoRenderer


def test_registry_has_all_renderers() -> None:
    registry = RendererRegistry()
    assert len(registry._renderers) == 28


def test_stat_renderer_detection() -> None:
    renderer = StatRenderer()
    assert renderer.can_render(Path("/proc/1/stat"))


def test_statm_renderer_detection() -> None:
    renderer = StatmRenderer()
    assert renderer.can_render(Path("/proc/1/statm"))


def test_status_renderer_detection() -> None:
    renderer = StatusRenderer()
    assert renderer.can_render(Path("/proc/1/status"))
    assert not renderer.can_render(Path("/proc/meminfo"))


def test_cmdline_renderer_detection() -> None:
    renderer = CmdlineRenderer()
    assert renderer.can_render(Path("/proc/1/cmdline"))
    assert not renderer.can_render(Path("/proc/1"))


def test_environ_renderer_detection() -> None:
    renderer = EnvironRenderer()
    assert renderer.can_render(Path("/proc/1/environ"))


def test_limits_renderer_detection() -> None:
    renderer = LimitsRenderer()
    assert renderer.can_render(Path("/proc/1/limits"))


def test_namespaces_renderer_detection() -> None:
    renderer = NamespacesRenderer()
    assert renderer.can_render(Path("/proc/1/ns"))


def test_oom_score_renderer_detection() -> None:
    renderer = OomScoreRenderer()
    assert renderer.can_render(Path("/proc/1/oom_score"))


def test_oom_score_adj_renderer_detection() -> None:
    renderer = OomScoreAdjRenderer()
    assert renderer.can_render(Path("/proc/1/oom_score_adj"))


def test_mountinfo_renderer_detection() -> None:
    renderer = MountinfoRenderer()
    assert renderer.can_render(Path("/proc/1/mountinfo"))


def test_coredump_filter_renderer_detection() -> None:
    renderer = CoredumpFilterRenderer()
    assert renderer.can_render(Path("/proc/1/coredump_filter"))


def test_smaps_renderer_detection() -> None:
    renderer = SmapsRenderer()
    assert renderer.can_render(Path("/proc/1/smaps"))


def test_numa_maps_renderer_detection() -> None:
    renderer = NumaMapsRenderer()
    assert renderer.can_render(Path("/proc/1/numa_maps"))


def test_attr_renderer_detection() -> None:
    renderer = AttrRenderer()
    assert renderer.can_render(Path("/proc/1/attr"))


def test_cgroup_renderer_detection() -> None:
    renderer = CgroupRenderer()
    assert renderer.can_render(Path("/proc/1/cgroup"))


def test_task_renderer_detection() -> None:
    renderer = TaskRenderer()
    assert renderer.can_render(Path("/proc/1/task"))


def test_net_tcp_renderer_detection() -> None:
    renderer = NetTcpRenderer()
    assert renderer.can_render(Path("/proc/1/net/tcp"))


def test_net_udp_renderer_detection() -> None:
    renderer = NetUdpRenderer()
    assert renderer.can_render(Path("/proc/1/net/udp"))


def test_net_unix_renderer_detection() -> None:
    renderer = NetUnixRenderer()
    assert renderer.can_render(Path("/proc/1/net/unix"))


def test_net_dev_renderer_detection() -> None:
    renderer = NetDevRenderer()
    assert renderer.can_render(Path("/proc/1/net/dev"))


def test_symlink_renderer_detection() -> None:
    renderer = SymlinkRenderer()
    assert renderer.can_render(Path("/proc/1/ns/net"))


def test_fd_renderer_detection() -> None:
    renderer = FdRenderer()
    assert renderer.can_render(Path("/proc/1/fd"))
    assert not renderer.can_render(Path("/proc/1/fds"))


def test_maps_renderer_detection() -> None:
    renderer = MapsRenderer()
    assert renderer.can_render(Path("/proc/991/maps"))


def test_io_renderer_detection() -> None:
    renderer = IoRenderer()
    assert renderer.can_render(Path("/proc/412/io"))


def test_sched_renderer_detection() -> None:
    renderer = SchedRenderer()
    assert renderer.can_render(Path("/proc/1/sched"))


def test_meminfo_renderer_detection() -> None:
    renderer = MemInfoRenderer()
    assert renderer.can_render(Path("/proc/meminfo"))


def test_cpuinfo_renderer_detection() -> None:
    renderer = CpuInfoRenderer()
    assert renderer.can_render(Path("/proc/cpuinfo"))


def test_text_renderer_smart_key_value() -> None:
    renderer = TextRenderer()
    result = renderer.render(Path("/proc/1/somefile"), "Name: proc\nPid: 1\nState: S (sleeping)")
    assert isinstance(result, Panel)


def test_text_renderer_smart_numeric() -> None:
    renderer = TextRenderer()
    result = renderer.render(Path("/proc/1/oom_score"), "234")
    assert isinstance(result, Panel)


def test_text_renderer_smart_table() -> None:
    renderer = TextRenderer()
    result = renderer.render(Path("/proc/1/net/route"), "Iface Destination Gateway Flags RefCnt Use Metric Mask MTU Window IRTT\neth0 00000000 00000000 0003 0 0 0 00000000 0 0 0")
    assert isinstance(result, Panel)
