"""
Weave configuration and initialization utilities.

This module provides centralized Weave configuration to prevent
logging errors and I/O issues during testing and development.
"""

import logging
import os

try:
    import weave
    WEAVE_AVAILABLE = True
except ImportError:
    WEAVE_AVAILABLE = False
    weave = None

from app.core.config import settings


def configure_weave_logging():
    """Configure logging to suppress Weave print statements."""
    # Set environment variables to disable problematic features
    os.environ.setdefault("WEAVE_PRINT_CALL_LINK", "false")

    # Configure logging to suppress Weave and Wandb logging
    logging.getLogger("weave").setLevel(logging.ERROR)
    logging.getLogger("wandb").setLevel(logging.ERROR)
    logging.getLogger("wandb.sdk").setLevel(logging.ERROR)


def init_weave_for_tests(project_name: str | None = None) -> bool:
    """
    Initialize Weave for testing with proper error handling.

    Args:
        project_name: Optional project name, defaults to test project

    Returns:
        True if initialization succeeded, False otherwise
    """
    if not WEAVE_AVAILABLE:
        return False

    configure_weave_logging()

    try:
        if project_name is None:
            project_name = f"{settings.WEAVE_PROJECT}-test"

        weave.init( project_name=project_name,)
        return True
    except Exception:
        # If weave init fails, continue without it for tests
        return False


def init_weave_for_production() -> bool:
    """
    Initialize Weave for production with proper error handling.

    Returns:
        True if initialization succeeded, False otherwise
    """
    if not WEAVE_AVAILABLE:
        return False

    configure_weave_logging()

    try:
        weave.init( settings.WEAVE_PROJECT)
        return True
    except Exception:
        # If weave init fails, continue without it
        return False


def get_weave_op_decorator():
    """
    Get a safe weave.op decorator that handles errors gracefully.

    Returns:
        A decorator function that can be used instead of @weave.op()
    """
    def safe_weave_op(func):
        """Safe weave.op decorator that doesn't fail if Weave is not available."""
        if not WEAVE_AVAILABLE:
            return func

        try:
            return weave.op()(func)
        except Exception:
            # If weave is not available, return the function unchanged
            return func
    return safe_weave_op
