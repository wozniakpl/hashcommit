import subprocess
from typing import Dict, List, Optional


def run_subprocess(
    args: List[str], env: Optional[Dict] = None, check: bool = True
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )
