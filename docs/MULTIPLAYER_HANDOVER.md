# Critter Lab — integration handover

The source of truth is the bundled `manifest.json` and `assets/{heads,bodies,legs}/*.svg`. The current multiplayer application is **not** changed by this repository.

During Pass 2, design a standalone offline character creator. The student can accept a random starter immediately, select each animal part, recolour individual parts, and save the avatar locally.

For eventual multiplayer integration, send only an allowlisted object with `head`, `body`, `legs` and palette IDs, not raw SVG or images. Validate server-side and clamp the encoded length. Preserve the avatar during reconnects, show it in roster/leaderboard, and keep existing nicknames, teacher controls, scores, team logic, and mathematical awards intact.

Suggested UI:
- Joining: optional rapid customisation, skippable.
- Lobby: full-body avatar on player card.
- Roster: head-focused icon at small sizes; preserve nickname readability.
- Awards: full-body critters on the existing teacher-controlled podium.
- Team identity: independent border/badge, not forced recolouring.
- Motion: subtle swaying or small bounce; honour `prefers-reduced-motion`.
- Keyboard and touch controls, visible focus, accessible labels, responsive 320px+ screens.

Test 45 students, reconnection after transient network loss, invalid/missing IDs, mobile and desktop layouts, duplicate display names and text alternatives. The parts must be fetched from the app's own origin only.