# Critter Lab — animal avatar artwork

A standalone development workspace for the planned animal avatar creator in [Sampling Arcade multiplayer](https://chriswalker-afk.github.io/Data-Collection/multiplayer.html).

The live Sampling Arcade repository and Cloudflare backend are **not changed** by this project. We will transfer the finished, approved feature only after it has been tested independently.

## Pass 1: modular SVG character library

- **8 heads:** fox, frog, panda, owl, rabbit, cat, penguin, dino
- **6 bodies:** penguin, dino, bear, cat, flamingo, owl
- **6 leg sets:** frog, duck, rabbit, cat, flamingo, dino
- **6 palettes** in `manifest.json`; separate colour choices are supported for each layer.
- **288 base critters**, or **62,208** when each layer independently chooses one of the six palettes.

Each illustration is original editable source artwork, not a crop from a PNG. All SVGs share `viewBox="0 0 320 360"` and are composited in order **legs → body → head** at a common origin. The neck join is at y≈154 and the waist join at y≈260.

### Inspect the art

The standalone `index.html` is a static gallery using the actual SVG layers. Open it through a local server (`python3 -m http.server 4173`) or through GitHub Pages after Pages is enabled for this repository. It is **not yet** an interactive character creator.

### Compose an SVG

```bash
python3 scripts/compose_avatar.py --head fox --body penguin --legs frog --output fox-penguin-frog.svg
python3 scripts/compose_avatar.py --head panda --body dino --legs duck --head-palette grape-purple --body-palette leaf-green --legs-palette honey-yellow --output colourful-critter.svg
```

### Validate the library

```bash
python3 -m pip install -r requirements-test.txt
python3 tests/validate_library.py
```

The original Pass 1 validation suite checks transparency and security, all 20 parts, 48 head/body seams, 36 body/leg seams, 288 basic combinations and 1,728 whole-avatar palette variants. GitHub Actions runs this suite on branches and PRs.

### Development plan

1. **Pass 1:** complete independent asset library and tests (this repository).
2. **Pass 2:** standalone responsive avatar customiser: selectable parts, independent colours, randomiser, local persistence.
3. **Pass 3:** combination, usability, mobile and accessibility audits.
4. **Pass 4:** multiplayer-ready lobby, roster and awards experience, plus integration handover.

See [asset contract](docs/PASS_1_ASSET_CONTRACT.md) and [multiplayer handover](docs/MULTIPLAYER_HANDOVER.md). Never load user-supplied SVG markup or permit avatars to influence scoring.
