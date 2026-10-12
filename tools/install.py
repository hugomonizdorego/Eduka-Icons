#!/usr/bin/env python3
"""Install only Eduka themes, optionally select a theme; existing settings are backed up."""
import argparse
import configparser
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def set_ini(path,section,key,value):
    cfg=configparser.ConfigParser(interpolation=None,strict=False)
    cfg.optionxform=str
    if path.exists():cfg.read(path)
    if section not in cfg:cfg.add_section(section)
    cfg[section][key]=value
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        shutil.copy2(path,path.with_name(path.name+'.eduka-backup-'+stamp))
    with path.open('w') as f:cfg.write(f,space_around_delimiters=False)

def apply(variant,system=False):
    theme=f'Eduka-Icons-{variant}'
    if system:
        if os.geteuid()!=0:raise SystemExit('System defaults require root.')
        config=Path('/etc/xdg')
    else:
        if os.geteuid()==0:raise SystemExit('Run user theme selection without sudo; use --system-defaults for an ISO.')
        config=Path(os.environ.get('XDG_CONFIG_HOME',Path.home()/'.config'))
    set_ini(config/'lxqt/lxqt.conf','General','icon_theme',theme)
    set_ini(config/'gtk-3.0/settings.ini','Settings','gtk-icon-theme-name',theme)
    set_ini(config/'gtk-4.0/settings.ini','Settings','gtk-icon-theme-name',theme)
    if not system and os.environ.get('DBUS_SESSION_BUS_ADDRESS') and shutil.which('gsettings'):
        # gsettings may be absent/unavailable inside a headless build container.
        subprocess.run(['gsettings','set','org.gnome.desktop.interface','icon-theme',theme],check=False)
    print(f'Selected {theme}. Log out and log in to refresh running applications.')

def migrate_local(system_icons=Path('/usr/share/icons')):
    """Back up local overrides before selecting an installed system release."""
    if os.geteuid()==0:raise SystemExit('Run --use-system-theme without sudo in the desktop account.')
    names=('Eduka-Icons-Light','Eduka-Icons-Dark')
    for name in names:
        cfg=configparser.ConfigParser(interpolation=None);cfg.read(system_icons/name/'index.theme')
        if cfg.get('Icon Theme','X-Eduka-Version',fallback='')!='0.3.0' or cfg.get('Icon Theme','X-Eduka-Edition',fallback='')!='Standalone':
            raise SystemExit('Install the standalone 0.3.0 DEB before using --use-system-theme.')
    data=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))
    roots={data/'icons',Path.home()/'.local/share/icons',Path.home()/'.icons'}
    targets=[]
    for root in roots:
        for name in names:
            p=root/name
            if p.is_symlink():raise SystemExit(f'Refusing to move a theme-directory symlink: {p}')
            if not p.exists():continue
            cfg=configparser.ConfigParser(interpolation=None);cfg.read(p/'index.theme')
            if cfg.get('Icon Theme','Name',fallback='')!=name:
                raise SystemExit(f'Unrecognised local theme directory: {p}')
            targets.append(p)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for i,p in enumerate(sorted(targets)):
        backup=data/'eduka-icons/backups'/stamp/str(i)/p.name
        backup.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(p),str(backup))
        print(f'Backed up local override: {backup}')
    print('System Eduka-Icons 0.3.0 is now available without local overrides.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--system',action='store_true',help='install to /usr/share/icons')
    p.add_argument('--destdir',type=Path,help='staging path, e.g. for a package build')
    p.add_argument('--apply',choices=['Light','Dark'])
    p.add_argument('--system-defaults',action='store_true',help='apply defaults under /etc/xdg, for Cubic/live ISO')
    p.add_argument('--select-only',action='store_true')
    p.add_argument('--use-system-theme',action='store_true',help='back up local Eduka overrides so the installed 0.3.0 DEB takes effect')
    a=p.parse_args()
    if (a.system or a.system_defaults) and os.geteuid()!=0:raise SystemExit('Use sudo for system installation/defaults.')
    if a.system_defaults and not a.apply:raise SystemExit('--system-defaults requires --apply Light or Dark.')
    if a.destdir and (a.apply or a.select_only):raise SystemExit('Staging installation does not change desktop settings.')
    if a.use_system_theme:
        if a.destdir or a.system or a.system_defaults:raise SystemExit('--use-system-theme applies only to a desktop user.')
        migrate_local()
        a.select_only=True
    if a.apply and os.geteuid()==0 and not a.system_defaults:raise SystemExit('Run user selection without sudo, or use --system-defaults for an ISO.')
    if not a.select_only:
        dest=a.destdir or (Path('/usr/share/icons') if a.system else Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'icons')
        dest.mkdir(parents=True,exist_ok=True)
        for name in ['Eduka-Icons-Light','Eduka-Icons-Dark']:
            source=ROOT/'build/themes'/name
            if not (source/'index.theme').is_file():raise SystemExit('Run make build before installing from source.')
            target=dest/name
            if target.is_symlink():raise SystemExit(f'Refusing to overwrite a theme-directory symlink: {target}')
            if target.exists():
                stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
                target.rename(dest/(name+'.eduka-backup-'+stamp))
            shutil.copytree(source,target,symlinks=True)
            if shutil.which('gtk-update-icon-cache'):
                subprocess.run(['gtk-update-icon-cache','-f','-t',str(target)],check=True)
            print(f'Installed {name} at {target}')
    if a.apply:apply(a.apply,a.system_defaults)

if __name__=='__main__':main()
