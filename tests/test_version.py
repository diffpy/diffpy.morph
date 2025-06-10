"""Unit tests for __version__.py."""

import diffpy.morph


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(diffpy.morph, "__version__")
    assert diffpy.morph.__version__ != "0.0.0"
