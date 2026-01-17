"""
Tests for orchestrator.
"""

import pytest
from app.core.orchestrator import Orchestrator


def test_orchestrator_init():
    """Test orchestrator initialization."""
    orchestrator = Orchestrator()
    assert orchestrator is not None
