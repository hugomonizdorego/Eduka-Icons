"""Eduka clay assets (17 hero masters from 0.3.0 plus generated compositions)."""
import base64
import functools
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import io
from PIL import Image
import settings
from artwork import glyph, badge, folder_kind, mix
from art import OVERRIDES, BADGES, OVERLAYS

ROOT = Path(__file__).resolve().parents[1]
ASSETS = settings.BUILD / 'masters'
MATERIALS = {'tile':'#f1e4c9','ivory':'#f0e2c4','paper':'#f7ecd4','sky':'#a7c8c6',
 'blue':'#97bab9','cobalt':'#718a73','coral':'#df7541','honey':'#e5b652',
 'gold':'#c69b46','teal':'#91b6ae','mint':'#89965c','lavender':'#8d9870',
 'peach':'#d99261','ink':'#49453e','metal':'#b0b6a0','lens':'#494842', 'glass':'#779c98',
 # 1.0 detail palette (same clay family, more tonal steps)
 'cream':'#f4e8cf','cream-dark':'#d9c7a3','white':'#fbf5e6','olive':'#7d8c55','olive-dark':'#5f6c40',
 'aqua':'#8fc0c4','aqua-dark':'#6a9ea3','orange':'#e0703a','orange-dark':'#b9552a','yellow':'#eec14f',
 'yellow-dark':'#cf9f33','charcoal':'#3f3c37','rose':'#d98a7a','sand':'#e6d3ad','stone':'#9a9c8b'}

def definitions():
    gradients=[]
    for name,c in MATERIALS.items():
        gradients.append(f'<linearGradient id="{name}" x1=".15" y1="0" x2=".85" y2="1"><stop stop-color="{mix(c,"#fff5df",.24)}"/><stop offset=".45" stop-color="{c}"/><stop offset="1" stop-color="{mix(c,"#514a3b",.22)}"/></linearGradient>')
    data='<defs>'+''.join(gradients)+'''<filter id="clay" x="-18%" y="-18%" width="140%" height="146%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="1.7" result="height"/>
 <feDiffuseLighting in="height" surfaceScale="4.6" diffuseConstant="1.02" lighting-color="#fff6e6" result="light"><feDistantLight azimuth="232" elevation="54"/></feDiffuseLighting>
 <feComposite in="light" in2="SourceAlpha" operator="in" result="light"/>
 <feComposite in="SourceGraphic" in2="light" operator="arithmetic" k1="1.24" k2="0" k3="0" k4="0" result="shaded"/>
 <feGaussianBlur in="SourceAlpha" stdDeviation="1.1" result="tight"/>
 <feSpecularLighting in="tight" surfaceScale="3.2" specularConstant=".42" specularExponent="14" lighting-color="#fffaf0" result="spec"><feDistantLight azimuth="232" elevation="50"/></feSpecularLighting>
 <feComposite in="spec" in2="SourceAlpha" operator="in" result="spec"/>
 <feComposite in="shaded" in2="spec" operator="arithmetic" k1="0" k2="1" k3=".55" k4="0" result="lit"/>
 <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="17" result="grain"/>
 <feColorMatrix in="grain" type="saturate" values="0" result="grain"/>
 <feComposite in="grain" in2="SourceAlpha" operator="in" result="grain"/>
 <feComposite in="lit" in2="grain" operator="arithmetic" k1="0" k2=".955" k3=".045" k4="0" result="clayface"/>
 <feGaussianBlur in="SourceAlpha" stdDeviation="2.6" result="ambient"/>
 <feOffset in="ambient" dx="1.4" dy="3.4" result="ambient"/>
 <feFlood flood-color="#3b382d" flood-opacity=".16"/>
 <feComposite in2="ambient" operator="in" result="ambient"/>
 <feGaussianBlur in="SourceAlpha" stdDeviation=".8" result="contact"/>
 <feOffset in="contact" dx=".6" dy="1.3" result="contact"/>
 <feFlood flood-color="#3b382d" flood-opacity=".2"/>
 <feComposite in2="contact" operator="in" result="contact"/>
 <feMerge><feMergeNode in="ambient"/><feMergeNode in="contact"/><feMergeNode in="clayface"/></feMerge>
 </filter></defs>'''
    original=data[data.index('<filter'):data.index('</filter>')+len('</filter>')]
    stroke=original.replace('id="clay" x="-18%" y="-18%" width="140%" height="146%"', 'id="clay-stroke" filterUnits="userSpaceOnUse" x="-8" y="-8" width="144" height="148"')
    return data.replace('</defs>',stroke+'</defs>')

def soften(art):
    # Restrict every literal decorative colour to the reference palette.
    def recolor(m):
        c=m[0];rgb=tuple(int(c[i:i+2],16) for i in (1,3,5))
        if max(rgb)<100:return MATERIALS['ink']
        if min(rgb)>190:return MATERIALS['paper']
        if rgb[2]>rgb[0]:return MATERIALS['sky']
        if rgb[1]>rgb[0]*1.05:return MATERIALS['mint']
        if rgb[0]>rgb[2]*1.3:return MATERIALS['honey'] if rgb[1]>150 else MATERIALS['coral']
        return MATERIALS['metal']
    return re.sub(r'#[0-9a-fA-F]{6}\b',recolor,art)

def vector(kind,size=1024):
    # Freestanding geometry, independently sculpted paper/books are new here.
    if kind in OVERRIDES:art=OVERRIDES[kind]()   # 1.0 detailed artwork, already on palette
    elif kind=='book':
        art='''<path d="M17 33Q35 23 63 34Q89 23 111 33V96Q84 86 64 98Q40 85 17 96Z" fill="url(#mint)"/>
        <path d="M21 28Q44 20 63 32V91Q44 80 21 89Z" fill="url(#paper)"/>
        <path d="M65 32Q91 20 107 29V89Q83 80 65 91Z" fill="url(#ivory)"/>
        <path d="M64 33V92" stroke="#c7b992" stroke-width="3" stroke-linecap="round"/>
        <path d="M30 42Q43 38 53 43M30 53Q43 49 53 54M76 42Q88 37 98 42M76 53Q88 48 98 53" fill="none" stroke="#89965c" stroke-width="3" stroke-linecap="round"/>
        <path d="M80 67H91V97L85 91L80 97Z" fill="url(#coral)"/>'''
    elif kind in OVERRIDES:art=OVERRIDES[kind]()   # 1.0 detailed artwork, already on palette
    else:art=soften(glyph(kind))
    # Sculpt each component, rather than lighting only the outer silhouette.
    fragment=ET.fromstring('<g>'+art+'</g>')
    for el in fragment.iter():
        if el.tag in ('path','rect','circle','ellipse','polygon'):
            el.set('filter','url(#clay-stroke)' if el.get('fill')=='none' else 'url(#clay)')
    art=ET.tostring(fragment,encoding='unicode')
    art=f'<g transform="translate(-9 -9) scale(1.14)">{art}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 128 128">{definitions()}{art}</svg>'

@functools.lru_cache(maxsize=1200)
def encoded(name,size=1024):
    with Image.open(ASSETS/(name+'.png')) as im:
        im=im.convert('RGBA')
        if im.size!=(size,size):im=im.resize((size,size),Image.Resampling.LANCZOS)
        out=io.BytesIO();im.save(out,format='PNG')
    return base64.b64encode(out.getvalue()).decode()

def image_svg(name,size=128,embedded_size=None):
    resolution=embedded_size or size
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{size}" height="{size}" viewBox="0 0 {size} {size}"><image width="{size}" height="{size}" xlink:href="data:image/png;base64,{encoded(name,resolution)}"/></svg>\n'

KIND_ASSET={'gear':'settings','doc-text':'document','book':'book','camera':'camera','browser':'browser','terminal':'terminal','home':'home','folder':'folder'}

def source_for(name,kind):
    if kind in OVERLAYS:return kind
    if name=='edukasaun' or name=='applications-education':return 'education'
    if name=='system-file-manager':return 'files'
    if kind.startswith('folder-'):return kind
    return KIND_ASSET.get(kind,kind)

def svg(kind,color='cream',variant='Light',size=128):
    return image_svg(KIND_ASSET.get(kind,kind),size)

def folder_svg(kind,size=1024):
    image=f'<image width="128" height="128" href="data:image/png;base64,{encoded("folder")}"/>'
    if kind in ('plain','folder'):return image_svg('folder',size)
    art=BADGES[kind]() if kind in BADGES else soften(badge(kind))
    symbol='<g transform="translate(56 43) scale(.6)">'+art+'</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 128 128">{definitions()}{image}<g filter="url(#clay)"><circle cx="94" cy="92" r="18" fill="url(#mint)"/>{symbol}</g></svg>'


def overlay_svg(asset,size=1024):
    """State variant: clay fragment composited over a hero master (see tools/art/states.py)."""
    base,fragment=OVERLAYS[asset]
    image=f'<image width="128" height="128" href="data:image/png;base64,{encoded(base)}"/>'
    part=ET.fromstring('<g>'+fragment()+'</g>')
    for el in part.iter():
        if el.tag in ('path','rect','circle','ellipse','polygon'):
            el.set('filter','url(#clay-stroke)' if el.get('fill')=='none' else 'url(#clay)')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 128 128">{definitions()}{image}{ET.tostring(part,encoding="unicode")}</svg>'
