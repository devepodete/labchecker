import hashlib
import re
import subprocess
import os

from pathlib import Path
from typing import List


def get_file_size(file: Path) -> int:
    return file.stat().st_size


def get_files_size(files: List[Path]) -> int:
    return sum([get_file_size(file) for file in files])


def get_file_hash(file: Path) -> bytes:
    result = hashlib.md5()
    with open(file, 'r') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            result.update(chunk)

    return result.digest()


def process_exist(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


SIGN_FINGERPRINT_REGEXP = re.compile('.*using RSA key ([0-9A-Z]+).*')
KEY_FINGERPRINT_REGEXP = re.compile(R'^ +([0-9A-Z]+)$')


def signature_ok(file: Path, signature: Path, pubkey: Path) -> (bool, str):
    if not (file.exists() and signature.exists() and pubkey.exists()):
        return False, 'One of the files do not exist'

    proc = subprocess.run(['gpg', '--verify', str(signature), str(file)], stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE)
    if proc.returncode not in (0, 2):
        return False, 'gpg --verify returned bad code'

    matched = SIGN_FINGERPRINT_REGEXP.search(str(proc.stderr))
    if not matched or len(matched.groups()) != 1:
        return False, 'gpg --verify output does not match regexp'

    fingerprint1 = matched.groups()[0]

    proc = subprocess.run(['gpg', str(pubkey)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if proc.returncode != 0:
        return False, f'gpg {pubkey} returned non-zero code'

    out = str(proc.stdout).split(R'\n')
    if len(out) < 2:
        return False, f'Bad output length of gpg {pubkey}: {len(out)}'

    matched = KEY_FINGERPRINT_REGEXP.match(out[1])
    if not matched:
        return False, f'gpg {pubkey} does not match regexp'

    fingerprint2 = matched.groups()[0]

    return fingerprint1 == fingerprint2, ''
