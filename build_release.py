import os
from pathlib import Path
import subprocess
import sys
import time

from PyInstaller.archive.readers import CArchiveReader


ROOT = Path(__file__).resolve().parent
EXECUTABLE = ROOT / "dist" / "Animora.exe"


def main():
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "animora.spec"],
        cwd=ROOT,
        check=True,
    )
    if not EXECUTABLE.is_file():
        raise FileNotFoundError(f"Build did not create {EXECUTABLE}")

    archive_entries = {str(name).lower() for name in CArchiveReader(str(EXECUTABLE)).toc}
    if "python312.dll" not in archive_entries:
        raise RuntimeError("python312.dll is missing from the portable executable.")

    system_root = Path(os.environ["WINDIR"])
    environment = {
        **os.environ,
        "PATH": f"{system_root / 'System32'};{system_root}",
        "QT_QPA_PLATFORM": "offscreen",
    }
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    process = subprocess.Popen(
        [str(EXECUTABLE)],
        cwd=ROOT,
        env=environment,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    try:
        time.sleep(4)
        if process.poll() is not None:
            raise RuntimeError(f"Portable startup check exited with code {process.returncode}.")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    print(f"Portable build verified: {EXECUTABLE}")


if __name__ == "__main__":
    main()
