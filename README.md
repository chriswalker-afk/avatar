# Critter Lab — standalone animal avatar creator

Critter Lab is the **independent development sandbox** for the future [Sampling Arcade multiplayer](https://chriswalker-afk.github.io/Data-Collection/multiplayer.html) avatar feature. It does not connect to classroom rooms, scores, awards or the live Cloudflare backend. The live [Data-Collection](https://github.com/chriswalker-afk/Data-Collection) repository remains untouched.

## Pass 2: working character creator

Visit `index.html` using a local web server or GitHub Pages once Pages is enabled.

- Choose from **8 heads, 6 bodies and 6 leg sets** (288 core combinations).
- Choose **original artwork colours** or one of six palettes **independently for each layer** (62,208 combinations with the six non-original palettes, before original-colour variants).
- See an immediate, full-body SVG preview with a playful generated character name.
- Use **Surprise me!** to randomise parts and colours, or **Start again** to reset the entire creator.
- Your selection is automatically stored only in this browser under `critter-lab.avatar.v1`; it is restored on the next visit. If storage is disabled, creation still works and the message explains that nothing is saved.
- **Save artwork** exports one standalone, transparent SVG containing the selected head/body/leg shapes and colours. No upload is performed.
- Mobile, keyboard, screen-reader labels, system reduced-motion preferences, load failures and corrupted storage are covered.

### Try it locally

```bash
python3 -m http.server 4173
```

Open <http://localhost:4173/>. Do **not** open `index.html` using `file://`; browsers restrict the manifest and SVG resource requests for local files.

### Automated tests

```bash
npm run check
python3 -m pip install -r requirements-test.txt
python3 tests/validate_library.py
python3 -m pip install playwright
python3 -m playwright install chromium
python3 tests/browser_smoke.py
```

`npm run check` runs pure configuration tests, including all **288** animal combinations and **62,208** independent palette variations. The original Pass 1 artwork test covers all 20 SVGs and their seam geometry. Real Chromium smoke tests exercise saved/restored choices, keyboard/touch controls, 320px/390px/768px/1280px layouts, SVG export, failure/retry, reduced motion and browser storage failure. Both jobs run via GitHub Actions on pull requests.

### GitHub Pages preview

The root `index.html` and bundled assets are Pages-ready, with relative file paths. Pages needs to be enabled in **Settings → Pages**, choosing `Deploy from a branch`, `main`, `/ (root)`. Once published, the preview is expected at `https://chriswalker-afk.github.io/avatar/`. Do not assume it is active until GitHub reports a successful deployment.

## Asset format

- SVG assets: `assets/{heads,bodies,legs}/*.svg` (20 total).
- Manifest: `manifest.json` (parts, original colours, six palettes and anchors).
- Browser logic: `src/model.js` (pure configuration validation) and `src/app.js` (loading, SVG assembly, interaction and persistence).
- Styles: `src/creator.css`.
- Python composer: `scripts/compose_avatar.py`.

Every part has an identical transparent `viewBox="0 0 320 360"` and is assembled in this draw order: **legs → body → head**. Each selection is stored as a small, versioned and allowlisted JSON object:

```json
{
  "version": 1,
  "head": "fox",
  "body": "penguin",
  "legs": "frog",
  "colours": {
    "head": "grape-purple",
    "body": "original",
    "legs": "leaf-green"
  }
}
```

No names, authentication, student IDs, analytics or image uploads. The standalone browser's local storage is **not shared automatically** with a later website under a different origin; transferring the feature requires the multiplayer integration in Pass 4.

## Roadmap

1. **Pass 1 (merged)** — original compatible SVG artwork, six palettes and validations.
2. **Pass 2 (this pass)** — working and tested standalone character creator.
3. **Pass 3** — comprehensive composition / readability / touch / accessibility refinement; classroom usability feedback.
4. **Pass 4** — multiplayer lobby, roster and awards mockups, server-side allowlist and integration handover.

See [Pass 2 implementation notes](docs/PASS_2_CREATOR.md) and [the multiplayer handover](docs/MULTIPLAYER_HANDOVER.md).