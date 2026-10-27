# Pass 1 — Asset contract and compatibility

## Scope
Standalone, original vector source art for Critter Lab; **not** integrated with Sampling Arcade. Import the complete Pass 1 pack before starting Pass 2.

## Catalogue
- Heads (8): fox, frog, panda, owl, rabbit, cat, penguin, dino
- Bodies (6): penguin, dino, bear, cat, flamingo, owl
- Legs (6): frog, duck, rabbit, cat, flamingo, dino
- Colour palettes (6): sunset-orange, honey-yellow, leaf-green, ocean-teal, grape-purple, blossom-pink

## Artwork contract
Each SVG is transparent, self-contained and uses **viewBox="0 0 320 360"**. Every layer is positioned at the same origin, without cropping or independent scaling. Assemble in strict order **legs → body → head**. Anchors: x=160, neck y=154, waist y=260; overlapping joins are deliberate. Draw original silhouettes, not visible metal connectors.

Colour only elements labelled with `data-color-slot` or `data-stroke-slot`; permitted tokens are `primary`, `light`, `dark`, `belly`, `accent`, `spot`, `blush`. Leave eyes, highlights, outlines and untinted markings alone.

## Serialization contract (proposed)
```json
{
  "version": 1,
  "head": "fox",
  "body": "penguin",
  "legs": "frog",
  "colours": {
    "head": "grape-purple",
    "body": "ocean-teal",
    "legs": "leaf-green"
  }
}
```

Use only manifest-listed identifiers; reject or safely normalise unknown values on **both client and server**. Never accept arbitrary SVG input from players. Store a small identifier record rather than sending rendered SVG markup through WebSockets. No student account or personally identifying avatar metadata.

## Quality gates
1. All 20 parts load from bundled files with zero network dependencies.
2. All 48 head–body and 36 body–leg pairings overlap at the expected joins.
3. All 288 base combinations render correctly; all six palettes and independent-part recolouring validate.
4. Transparent SVGs have no embedded scripts, event handlers or external URLs.
5. Previews remain clear at 48px/64px/96px; use larger sizes for podium displays.
6. The build and source assets stay reproducible, and tests run in GitHub Actions.

Next: Pass 2 creator UI—responsive selections, safe colours, randomiser and local persistence. Preserve Sampling Arcade separately until approved.