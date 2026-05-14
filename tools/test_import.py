#!/usr/bin/env python
"""Quick test to verify all imports work."""

try:
    from pview.renderers.stat_renderer import StatRenderer
    print("✓ StatRenderer")
except Exception as e:
    print(f"✗ StatRenderer: {e}")

try:
    from pview.renderers.statm_renderer import StatmRenderer
    print("✓ StatmRenderer")
except Exception as e:
    print(f"✗ StatmRenderer: {e}")

try:
    from pview.renderers.limits_renderer import LimitsRenderer
    print("✓ LimitsRenderer")
except Exception as e:
    print(f"✗ LimitsRenderer: {e}")

try:
    from pview.renderers.namespaces_renderer import NamespacesRenderer
    print("✓ NamespacesRenderer")
except Exception as e:
    print(f"✗ NamespacesRenderer: {e}")

try:
    from pview.renderers.oom_score_renderer import OomScoreRenderer
    print("✓ OomScoreRenderer")
except Exception as e:
    print(f"✗ OomScoreRenderer: {e}")

try:
    from pview.renderers.mountinfo_renderer import MountinfoRenderer
    print("✓ MountinfoRenderer")
except Exception as e:
    print(f"✗ MountinfoRenderer: {e}")

try:
    from pview.renderers.smaps_renderer import SmapsRenderer
    print("✓ SmapsRenderer")
except Exception as e:
    print(f"✗ SmapsRenderer: {e}")

try:
    from pview.renderers.coredump_filter_renderer import CoredumpFilterRenderer
    print("✓ CoredumpFilterRenderer")
except Exception as e:
    print(f"✗ CoredumpFilterRenderer: {e}")

try:
    from pview.renderers.registry import RendererRegistry
    reg = RendererRegistry()
    print(f"✓ RendererRegistry loaded with {len(reg._renderers)} renderers")
except Exception as e:
    print(f"✗ RendererRegistry: {e}")

print("\n✓ All imports successful!")
