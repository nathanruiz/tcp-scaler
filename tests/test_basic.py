"""Basic tests that ensure the base project is stuctured properly."""

import os
import pytest

def test_import():
    """
    Verify we can import the tcp_scaler module. This will verify all the
    libraries required by tcp_scaler are install, and there are no syntax errors
    in the files loaded by the module.
    """
    import tcp_scaler
    assert hasattr(tcp_scaler, "main")

def test_no_pkg_resources():
    """Verify pkg-resources doesn't exist in the requirements.txt file."""
    with open("requirements.txt") as f:
        for line in f:
            assert not line.startswith("pkg-resources"), \
                "Found pkg-resources in requirements.txt"
