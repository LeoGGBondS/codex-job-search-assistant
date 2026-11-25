#!/usr/bin/env python3
# Check versioned/staged publishing content, not ignored local candidate data.
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TOP = {'AGENTS.md', 'README.md', 'README_CN.md', 'LICENSE', '.gitignore', '.gitattributes', 'requirements.txt',
               '.agents', '.github', 'scripts', 'tests', 'examples'}
PRIVATE_DIRS = {'personal', 'outputs', 'work', '.venv', 'venv', '__pycache__'}
BINARY_SUFFIXES = {'.pdf', '.doc', '.docx', '.rtf', '.png', '.jpg', '.jpeg', '.zip', '.pyc'}
SECRET_PATTERNS = [re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),
                   re.compile(r'sk-(?:proj-)?[A-Za-z0-9_-]{25,}'),
                   re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def inspect_paths(paths, staged=False):
    errors = []
    for relative in paths:
        path = ROOT / relative
        parts = Path(relative).parts
        if not parts or parts[0] not in ALLOWED_TOP or any(p in PRIVATE_DIRS for p in parts):
            errors.append('Not in public source allowlist: ' + relative)
            continue
        if path.is_symlink() or path.suffix.lower() in BINARY_SUFFIXES:
            errors.append('Private/binary/symlink asset: ' + relative)
            continue
        if not staged and not path.is_file():
            continue
        try:
            if staged:
                blob = subprocess.run(['git', '-C', str(ROOT), 'show', ':' + relative.replace(chr(92), '/')], capture_output=True, check=True).stdout
                text = blob.decode('utf-8-sig')
            else:
                text = path.read_text(encoding='utf-8-sig')
        except (UnicodeError, OSError, subprocess.CalledProcessError):
            errors.append('Unreadable text source: ' + relative)
            continue
        if any(p.search(text) for p in SECRET_PATTERNS):
            errors.append('Potential secret in: ' + relative)
        emails = EMAIL.findall(text)
        if any(not x.lower().endswith(('@example.invalid', '@example.com')) for x in emails):
            errors.append('Non-example email in: ' + relative)
        # Publisher-local absolute paths must never become installation defaults.
        if re.search(r'[A-Za-z]:[/\\]Users[/\\]', text) or re.search(r'/(?:Users|home)/', text):
            errors.append('Machine-specific home path in: ' + relative)
    return errors


def main():
    result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    staged = result.returncode == 0 and Path(result.stdout.strip()).resolve() == ROOT
    if staged:
        files = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached'], capture_output=True, check=True).stdout.decode().split('\0')
        paths = [p for p in files if p]
    else:
        paths = [str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()
                 and not any(part in PRIVATE_DIRS | {'.git'} for part in p.relative_to(ROOT).parts)]
    if not paths:
        print('No public source files to inspect; stage the intended source files first.')
        return 1
    errors = inspect_paths(paths, staged=staged)
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'Public-source preflight passed: {len(paths)} text files. Review the staged diff before publishing.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

