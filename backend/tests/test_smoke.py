from pathlib import Path
import subprocess
import sys


def test_dairy_core_imports_without_django():
    backend_dir = Path(__file__).resolve().parents[1]

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import dairy_core; "
            "assert 'django' not in sys.modules, 'dairy_core imported Django'",
        ],
        cwd=backend_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr