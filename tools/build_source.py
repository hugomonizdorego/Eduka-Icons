#!/usr/bin/env python3
"""Package only reusable source; build output and binary packages are excluded."""
import argparse
import gzip
import json
from pathlib import Path
import tarfile
import zipfile
from check_source import ROOT, LIMIT, check

def build(output):
    files, report = check()
    if report['errors']: raise SystemExit(json.dumps(report['errors']))
    output.mkdir(parents=True, exist_ok=True)
    stem = 'Eduka-Icons-0.3.0-GitHub-source'
    prefix = 'Eduka-Icons'
    zip_path = output / (stem + '.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo(prefix + '/' + path.relative_to(ROOT).as_posix(), (2026, 10, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 << 16)
            archive.writestr(info, path.read_bytes())
    tar_path = output / (stem + '.tar.gz')
    with tar_path.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', dereference=True) as archive:
            for path in files:
                info = archive.gettarinfo(str(path), arcname=prefix + '/' + path.relative_to(ROOT).as_posix())
                info.uid = info.gid = 0
                info.uname = info.gname = ''
                info.mtime = 0
                info.mode = 0o644
                with path.open('rb') as content: archive.addfile(info, content)
    for path in (zip_path, tar_path):
        if path.stat().st_size >= LIMIT: raise SystemExit('Source archive exceeds the 25 MiB browser upload target.')
    report['archives'] = {p.name: p.stat().st_size for p in (zip_path, tar_path)}
    (output / 'Eduka-Icons-0.3.0-source-size.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    build(parser.parse_args().output)
