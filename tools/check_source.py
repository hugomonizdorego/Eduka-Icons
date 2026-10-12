#!/usr/bin/env python3
"""Check the source allowlist and browser-compatible GitHub file sizes."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = ('README.md', 'CHANGELOG.md', 'LICENSE', 'VERSION', 'Makefile',
             'requirements.txt', '.gitignore', '.gitattributes')
VERSION = (ROOT / 'VERSION').read_text().strip() if (ROOT / 'VERSION').is_file() else ''
TOP_DIRECTORIES = ('tools', 'assets', 'docs', '.github')
LIMIT = 25 * 1024 * 1024

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
    result = {'version': VERSION, 'edition': 'Standalone', 'source_files': len(files),
              'total_bytes': sum(p.stat().st_size for p in files if p.is_file()),
              'largest_file_bytes': max((p.stat().st_size for p in files if p.is_file()), default=0),
              'errors': errors}
    return files, result

if __name__ == '__main__':
    _, result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
