"""Renderer registry for proc entries."""

from __future__ import annotations

from pathlib import Path

from rich.console import RenderableType

from pview.renderers.attr_renderer import AttrRenderer
from pview.renderers.cgroup_renderer import CgroupRenderer
from pview.renderers.cmdline_renderer import CmdlineRenderer
from pview.renderers.coredump_filter_renderer import CoredumpFilterRenderer
from pview.renderers.numa_maps_renderer import NumaMapsRenderer
from pview.renderers.oom_score_adj_renderer import OomScoreAdjRenderer
from pview.renderers.cpuinfo_renderer import CpuInfoRenderer
from pview.renderers.environ_renderer import EnvironRenderer
from pview.renderers.fd_renderer import FdRenderer
from pview.renderers.io_renderer import IoRenderer
from pview.renderers.limits_renderer import LimitsRenderer
from pview.renderers.maps_renderer import MapsRenderer
from pview.renderers.meminfo_renderer import MemInfoRenderer
from pview.renderers.mountinfo_renderer import MountinfoRenderer
from pview.renderers.namespaces_renderer import NamespacesRenderer
from pview.renderers.oom_score_renderer import OomScoreRenderer
from pview.renderers.sched_renderer import SchedRenderer
from pview.renderers.smaps_renderer import SmapsRenderer
from pview.renderers.stat_renderer import StatRenderer
from pview.renderers.statm_renderer import StatmRenderer
from pview.renderers.symlink_renderer import SymlinkRenderer
from pview.renderers.task_renderer import TaskRenderer
from pview.renderers.net_tcp_renderer import NetTcpRenderer
from pview.renderers.net_udp_renderer import NetUdpRenderer
from pview.renderers.net_unix_renderer import NetUnixRenderer
from pview.renderers.net_dev_renderer import NetDevRenderer
from pview.renderers.status_renderer import StatusRenderer
from pview.renderers.text_renderer import TextRenderer


class RendererRegistry:
    """Ordered list of renderers with fallback selection."""

    def __init__(self) -> None:
        self._renderers = [
            StatRenderer(),
            StatmRenderer(),
            StatusRenderer(),
            CmdlineRenderer(),
            EnvironRenderer(),
            LimitsRenderer(),
            NamespacesRenderer(),
            OomScoreRenderer(),
            OomScoreAdjRenderer(),
            MountinfoRenderer(),
            CoredumpFilterRenderer(),
            SmapsRenderer(),
            NumaMapsRenderer(),
            AttrRenderer(),
            CgroupRenderer(),
            TaskRenderer(),
            NetTcpRenderer(),
            NetUdpRenderer(),
            NetUnixRenderer(),
            NetDevRenderer(),
            SymlinkRenderer(),
            FdRenderer(),
            MapsRenderer(),
            IoRenderer(),
            SchedRenderer(),
            MemInfoRenderer(),
            CpuInfoRenderer(),
            TextRenderer(),
        ]

    def render(self, path: Path, content: str | None) -> RenderableType:
        for renderer in self._renderers:
            if renderer.can_render(path):
                return renderer.render(path, content)
        return TextRenderer().render(path, content)
