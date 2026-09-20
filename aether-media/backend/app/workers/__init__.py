"""
Background workers module.

Provides background task processors for:
- Media scanning
- Metadata fetching
- Cleanup jobs
"""

from app.workers.scanner import (
    run_scan,
    scan_all_libraries,
    MediaScanner,
)

__all__ = [
    "run_scan",
    "scan_all_libraries",
    "MediaScanner",
]
