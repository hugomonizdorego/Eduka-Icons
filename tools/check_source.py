#!/usr/bin/env python3
"""Check the source allowlist and browser-compatible GitHub file sizes."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = ('README.md', 'CHANGELOG.md', 'LICENSE', 'VERSION', 'Makefile',
             'requirements.txt', '.gitignore', '.gitattributes', 'eduka-icons.toml')
VERSION = (ROOT / 'VERSION').read_text().strip() if (ROOT / 'VERSION').is_file() else ''
TOP_DIRECTORIES = ('tools', 'assets', 'docs', '.github')
LIMIT = 25 * 1024 * 1024
RELEASE_LIMIT = 100 * 1024 * 1024      # GitHub rejects larger files

def source_files():
    files = [ROOT / name for name in TOP_FILES]
    for name in TOP_DIRECTORIES:
        files.extend(p for p in (ROOT / name).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    return sorted(files)

def check():
    files = source_files()
    errors = []
    for path in files:
        if not path.is_file(): errors.append(f'Missing source: {path.relative_to(ROOT)}')
        elif path.is_symlink(): errors.append(f'Source symlink: {path.relative_to(ROOT)}')
        elif path.stat().st_size >= LIMIT: errors.append(f'GitHub browser size limit: {path.relative_to(ROOT)}')
        relative = path.relative_to(ROOT)
        vendored = relative.parts[:2] == ('assets', 'upstream')
        if 'papirus' in str(relative).lower() and not vendored:
            errors.append(f'Upstream icon files outside assets/upstream: {relative}')
        if path.suffix.lower() in ('.deb', '.tar', '.gz', '.zip', '.xz', '.cache') and not vendored:
            errors.append(f'Build artifact in source: {path.relative_to(ROOT)}')
    # Everything git tracks must be a known source file or a release package.
    try:
        tracked = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z'], capture_output=True, check=True,
                                 timeout=30).stdout.decode('utf-8', 'surrogateescape').split('\0')
    except (OSError, subprocess.SubprocessError):
        tracked = []
    known = {str(path.relative_to(ROOT)) for path in files}
    for name in filter(None, tracked):
        path = ROOT / name
        if name in known or not path.exists():
            continue
        if Path(name).parts[0] == 'release' and path.suffix == '.deb':
            if path.stat().st_size >= RELEASE_LIMIT: errors.append(f'Release package over 100 MB: {name}')
            if f'_{VERSION}_' not in path.name: errors.append(f'Release package of another version: {name}')
        else:
            errors.append(f'Tracked file outside the source allowlist: {name}')
    result = {'version': VERSION, 'edition': 'Standalone', 'source_files': len(files),
              'total_bytes': sum(p.stat().st_size for p in files if p.is_file()),
              'largest_file_bytes': max((p.stat().st_size for p in files if p.is_file()), default=0),
              'errors': errors}
    return files, result

if __name__ == '__main__':
    _, result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
