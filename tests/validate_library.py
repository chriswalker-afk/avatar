#!/usr/bin/env python3
"""Automated asset validation, compositional seam audit, and palette coverage."""
from pathlib import Path
from xml.etree import ElementTree as ET
from itertools import product
import sys,io,json,hashlib,re
import cairosvg
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from compose_avatar import compose,MANIFEST
NAMESPACE='{http://www.w3.org/2000/svg}'
results=[]
def audit(name, condition,detail=''):
    if not condition: raise AssertionError(f'{name}: {detail}')
    results.append(name)


def png_mask(source,width=160,height=180):
    data=cairosvg.svg2png(bytestring=source.encode(),output_width=width,output_height=height)
    im=Image.open(io.BytesIO(data)).convert('RGBA')
    alpha=np.asarray(im)[:,:,3]
    return alpha

palette_names=list(MANIFEST['palettes'])
color_slots=set(MANIFEST['colorTokens'])
parts={}
for kind,choices in MANIFEST['parts'].items():
    for name in choices:
        f=ROOT/'assets'/kind/f'{name}.svg'
        audit('file-'+kind+'-'+name, f.exists() and f.stat().st_size < 15000)
        xml=f.read_text()
        audit('no-external-or-script-'+kind+'-'+name,not any(x in xml.lower() for x in ['<script','<foreignobject','http://www.w3.org/1999/xlink','url(http','onload=','onclick=','<image ']))
        tree=ET.fromstring(xml)
        audit('viewbox-'+kind+'-'+name,tree.attrib.get('viewBox')=='0 0 320 360')
        audit('root-size-'+kind+'-'+name,tree.attrib.get('width')=='320' and tree.attrib.get('height')=='360')
        audit('anchor-'+kind+'-'+name,tree.attrib.get('data-anchor-x')=='160' and tree.attrib.get('data-anchor-body-bottom-y')=='260')
        audit('accessible-title-'+kind+'-'+name,tree.find(NAMESPACE+'title') is not None and tree.find(NAMESPACE+'desc') is not None)
        audit('transparent-background-'+kind+'-'+name,not re.search(r'<rect\b[^>]+(?:width="320"|width="100%")',xml))
        tagged=list(tree.findall('.//*[@data-color-slot]'))
        audit('recolour-slots-'+kind+'-'+name,bool(tagged) and all(node.get('data-color-slot') in color_slots for node in tagged))
        audit('stroke-recolour-slots-'+kind+'-'+name,all(node.get('data-stroke-slot') in color_slots for node in tree.findall('.//*[@data-stroke-slot]')))
        alpha=png_mask(xml)
        audit('non-empty-alpha-'+kind+'-'+name,alpha.max()>0 and np.count_nonzero(alpha>100)>500)
        ys,xs=np.where(alpha>90)
        audit('no-canvas-clipping-'+kind+'-'+name, len(xs)>0 and xs.min()>0 and xs.max()<159 and ys.min()>0 and ys.max()<179, str((xs.min(),xs.max(),ys.min(),ys.max())))
        parts[kind,name]=alpha>80

head_body_overlaps={}
for h,b in product(MANIFEST['parts']['heads'],MANIFEST['parts']['bodies']):
    count=np.count_nonzero(parts['heads',h] & parts['bodies',b])
    head_body_overlaps[h,b]=int(count)
    audit('head-body-seam-'+h+'-'+b,count>=70,f'only {count} overlapping pixels')
body_legs_overlaps={}
for b,l in product(MANIFEST['parts']['bodies'],MANIFEST['parts']['legs']):
    count=np.count_nonzero(parts['bodies',b] & parts['legs',l])
    body_legs_overlaps[b,l]=int(count)
    audit('body-legs-seam-'+b+'-'+l,count>=70,f'only {count} overlapping pixels')

# Every base combination and every whole-character colourway is serializable,
# entirely local, and retains three independent editable parts.
count=0
for h,b,l in product(MANIFEST['parts']['heads'],MANIFEST['parts']['bodies'],MANIFEST['parts']['legs']):
    xml=compose(h,b,l)
    root=ET.fromstring(xml)
    parts_here=list(root.findall(NAMESPACE+'g'))
    audit('composition-'+h+'-'+b+'-'+l,len(parts_here)==3 and all(len(p)>0 for p in parts_here))
    audit('draw-order-'+h+'-'+b+'-'+l,[p.get('id') for p in parts_here]==['critter-legs','critter-bodies','critter-heads'])
    count+=1
palette_count=0
for h,b,l in product(MANIFEST['parts']['heads'],MANIFEST['parts']['bodies'],MANIFEST['parts']['legs']):
    for palette in palette_names:
        xml=compose(h,b,l,{'heads':palette,'bodies':palette,'legs':palette})
        root=ET.fromstring(xml)
        audit('palette'+str(palette_count),len(root.findall(NAMESPACE+'g'))==3)
        palette_count+=1
# Partial recolour needs to preserve untouched components.
a=compose('fox','bear','frog',{'heads':'grape-purple'})
b=compose('fox','bear','frog')
a_root=ET.fromstring(a);b_root=ET.fromstring(b)
a_head=a_root.findall(NAMESPACE+'g')[2];b_head=b_root.findall(NAMESPACE+'g')[2]
a_body=a_root.findall(NAMESPACE+'g')[1];b_body=b_root.findall(NAMESPACE+'g')[1]
audit('independent-color-tint', ET.tostring(a_head)!=ET.tostring(b_head) and ET.tostring(a_body)==ET.tostring(b_body))

# Static offline viewer should contain no broken local image/source references.
viewer=ROOT/'REVIEW.html'
if viewer.exists():
    viewer_html=viewer.read_text(encoding='utf-8')
    audit('review-no-scripts', '<script' not in viewer_html.lower())
    for i,ref in enumerate(re.findall(r'(?:src|href)="([^"]+)"',viewer_html)):
        if ref.startswith(('assets/','previews/','tests/')):
            audit('review-reference-'+str(i),(ROOT/ref).is_file(),ref)

audit('expected-part-count',sum(len(x) for x in MANIFEST['parts'].values())==20)
audit('expected-composition-count',count==288)
audit('expected-recolour-count',palette_count==1728)
summary={
    'status':'PASS',
    'totalAssertions':len(results),
    'totalIndividualAssets':sum(len(v) for v in MANIFEST['parts'].values()),
    'combinationsValidated':count,
    'wholeAvatarPaletteVariantsValidated':palette_count,
    'headBodySeamsValidated':len(head_body_overlaps),
    'bodyLegsSeamsValidated':len(body_legs_overlaps),
    'minimumHeadBodyOverlapPixelsAtHalfSize':min(head_body_overlaps.values()),
    'minimumBodyLegOverlapPixelsAtHalfSize':min(body_legs_overlaps.values()),
    'noRemoteAssets':True,
    'allTransparent':True,
    'allSameViewbox':True,
    'fileCount':sum(len(v) for v in MANIFEST['parts'].values())
}
(ROOT/'tests'/'validation_report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
