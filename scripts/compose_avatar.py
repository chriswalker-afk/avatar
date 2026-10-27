#!/usr/bin/env python3
"""Compose avatar as one transparent SVG, preserving editable, separate SVG groups."""
from pathlib import Path
from copy import deepcopy
from xml.etree import ElementTree as ET
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
SVGNS='http://www.w3.org/2000/svg'
ET.register_namespace('',SVGNS)
def tag(n): return f'{{{SVGNS}}}{n}'
MANIFEST=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))

def compose(head, body, legs, palettes=None):
    picks={'heads':head,'bodies':body,'legs':legs}
    for kind,name in picks.items():
        if name not in MANIFEST['parts'][kind]:
            raise ValueError(f'Unknown {kind}: {name}')
    palettes=palettes or {}
    root=ET.Element(tag('svg'), {'width':'320','height':'360','viewBox':'0 0 320 360','role':'img','aria-label':f'{head} head, {body} body and {legs} legs', 'data-critter-avatar':'1.0'})
    title=ET.SubElement(root,tag('title'));title.text=f'{head.title()} + {body.title()} + {legs.title()}'
    for kind in MANIFEST['drawOrder']:
        part_name=picks[kind]
        part_root=ET.parse(ROOT/'assets'/kind/(part_name+'.svg')).getroot()
        source=part_root.find(tag('g'))
        wrapped=ET.SubElement(root,tag('g'), {'id':f'critter-{kind}','data-part-id':part_name})
        group=deepcopy(source)
        group.attrib.pop('id',None)
        palette_name=palettes.get(kind)
        if palette_name:
            if palette_name not in MANIFEST['palettes']:
                raise ValueError(f'Unknown palette: {palette_name}')
            new_colors=MANIFEST['palettes'][palette_name]
            wrapped.set('data-palette-id',palette_name)
            for element in group.iter():
                slot=element.get('data-color-slot')
                if slot and slot in new_colors:
                    element.set('fill',new_colors[slot])
                stroke_slot=element.get('data-stroke-slot')
                if stroke_slot and stroke_slot in new_colors:
                    element.set('stroke',new_colors[stroke_slot])
        wrapped.append(group)
    return ET.tostring(root,encoding='unicode',xml_declaration=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--head',default='fox',choices=MANIFEST['parts']['heads'])
    p.add_argument('--body',default='penguin',choices=MANIFEST['parts']['bodies'])
    p.add_argument('--legs',default='frog',choices=MANIFEST['parts']['legs'])
    for k in ['head','body','legs']:
        p.add_argument('--'+k+'-palette',choices=list(MANIFEST['palettes']))
    p.add_argument('--output',default=str(ROOT/'previews'/'example-avatar.svg'))
    args=p.parse_args()
    palettes={'heads':args.head_palette,'bodies':args.body_palette,'legs':args.legs_palette}
    svg=compose(args.head,args.body,args.legs,{k:v for k,v in palettes.items() if v})
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(svg,encoding='utf-8')
    print(out)
