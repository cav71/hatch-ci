import subprocess
from functools import lru_cache


@lru_cache(maxsize=None)
def get_commit_hash(root: str):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode('utf-8').strip()
