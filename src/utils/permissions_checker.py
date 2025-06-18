import os
import stat
from pathlib import Path


def ensure_executable(path: Path):
    if not path.exists():
        print(f"[❌] File not found: {path}")
        return

    current_mode = path.stat().st_mode
    if not current_mode & stat.S_IXUSR:
        # Add execute permission for user (owner)
        os.chmod(path, current_mode | stat.S_IXUSR)
        print(f"[✔️] Executable permission added: {path}")
    else:
        print(f"[✅] Already executable: {path}")
