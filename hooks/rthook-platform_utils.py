# Runtime hook to fix platform_utils.paths.embedded_data_path() on macOS with PyInstaller
# The default implementation constructs a wrong path for PyInstaller app bundles

import sys

def _patched_embedded_data_path():
    """Return the correct embedded data path for PyInstaller."""
    # sys._MEIPASS is set by PyInstaller and points to the correct data directory
    # On macOS app bundles, this is Contents/Frameworks
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    # Fallback to app_path() for non-PyInstaller frozen apps
    from platform_utils.paths import app_path
    return app_path()

# Patch the function before any other modules use it
import platform_utils.paths
platform_utils.paths.embedded_data_path = _patched_embedded_data_path
