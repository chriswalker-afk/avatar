# Pass 2 — Interactive character creator handover

## Scope and verified behaviour

This pass replaces the Pass 1 static art gallery with a single-page, standalone creator. No server, classroom login, analytics, third-party images or external JavaScript. The UI loads the Pass 1 manifest and all 20 SVGs from same-origin relative URLs. Each layer is assembled from allowlisted assets at the existing 320×360 viewBox. A source validation pass rejects unknown element tags, unexpected attributes, mismatched IDs and external links. SVGs are recoloured only through documented data slots and embedded as decorative inline layers. The complete character has one accessible image label.

Control details:

- All options use real `<button>` elements, keyboard activation and `aria-pressed` states.
- Each part has seven colour choices: Original (retains the animal's natural design) plus six coordinated palettes.
- A live region announces part or colour changes. Status text confirms local saving or reports storage unavailability.
- Randomisation chooses head/body/legs and colours independently, avoiding a duplicate of the previous configuration.
- Reset restores Fox + Penguin + Frog and original colourways; saving happens immediately.
- Save artwork produces an editable standalone, transparent SVG; it is a browser download, not a server upload.
- Failed manifest/SVG fetches show a retry control without replacing the saved configuration.
- Reduced-motion users receive no floating or bounce animation.
- There is no connection to the real multiplayer room, lobby, roster or awards yet.

## Design choices

The classroom join flow must remain quick when integrated. Consequently the future student may accept the random default without opening this editor. The main screen uses a prominent preview and three independent option panels. At desktop widths, the preview remains visible while selecting animal parts; at tablet and mobile sizes it moves above the editor. Colours are selected by labelled swatches with a non-colour tick and separate text label.

## Data privacy and interoperability

Configuration is stored only in the browser, under `critter-lab.avatar.v1`. When the site is moved to `Data-Collection`, browser storage **will not transfer across origins** without an explicit, future import/export path. Never reuse an unvalidated JSON payload from local storage or WebSocket. During Pass 4, the server must enforce the same allowlisted part and palette identifiers and a bounded message size. Do not transmit downloaded SVG or generated HTML to the room.

## Testing and outstanding questions

The CI workflow runs Python SVG compatibility tests, JavaScript configuration tests for 288 base / 62,208 palette configurations, and real Chromium smoke checks at 320, 390, 768, 1280 and 1440 widths. It also checks save/restore, corrupt/disabled storage, keyboard and touch, reduced motion, randomisation, original palette restoration and SVG export. These are engineering checks rather than a substitute for student classroom feedback.

Pass 3 should audit small roster-size head previews, contrast for all palettes and user testing with a full classroom. Pass 4 integrates the accepted design into the multiplayer experience with no impact on fairness, teacher control or existing scoring.