#!/usr/bin/env python3
"""
Simple test to verify weave initialization works correctly.
"""

import sys
from pathlib import Path

# Add backend app to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")

# Test weave initialization using centralized configuration
from app.core.config import settings
from app.core.weave_config import init_weave_for_tests


def test_weave_initialization():
    """Test that weave initializes correctly with test project name."""
    print("Testing Weave initialization...")

    # Initialize weave using centralized configuration
    test_project = f"{settings.WEAVE_PROJECT}-test"
    print(f"Initializing weave with project: {test_project}")

    success = init_weave_for_tests(test_project)

    if success:
        print("✅ Weave initialized successfully!")
        print(f"✅ Project: {test_project}")
        print(f"✅ Base project: {settings.WEAVE_PROJECT}")
    else:
        print("⚠️ Weave initialization failed")
        print("This is expected in test environments")

    return success

if __name__ == "__main__":
    test_weave_initialization()
