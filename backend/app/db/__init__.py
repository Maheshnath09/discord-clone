"""Database helpers package.

Expose seeding helpers for the application.
"""

from .seed import ensure_demo_data

__all__ = ["ensure_demo_data"]