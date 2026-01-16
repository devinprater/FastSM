# Custom PyInstaller hook for sound_lib
# Overrides the default hook to exclude x86 binaries on macOS (they're i386/ppc only)

import sys
from pathlib import Path

binaries = []

if sys.platform == "darwin":
    # On macOS, only include x64 dylibs (these are universal binaries with arm64 support)
    # The x86 directory contains old i386/ppc binaries that are incompatible with arm64
    try:
        import sound_lib
        sl_path = Path(sound_lib.__file__).parent
        x64_lib = sl_path / "lib" / "x64"
        if x64_lib.exists():
            for dylib in x64_lib.glob("*.dylib"):
                binaries.append((str(dylib), "sound_lib/lib/x64"))
    except ImportError:
        pass
else:
    # On other platforms, use the default behavior
    from PyInstaller.utils.hooks import collect_dynamic_libs
    binaries = collect_dynamic_libs('sound_lib')
