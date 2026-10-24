# Minecraft Banner Tracker

A minimal Minecraft banner collection hosted on GitHub Pages.

[Open Banner Tracker](https://ryanehinkle.github.io/mc-banner-tracker/)

## Features

- Paste or drag a Minecraft Tools banner link to add it automatically.
- Preview the Minecraft banner pattern using bundled game textures.
- Edit names, open original crafting instructions, and mark banners made.
- Filter by All, To make, or Made. Counts match the visible collection.
- **Cross-device sync with no login and no token.** All devices read the same shared collection.

## Live sync architecture

- **Shared data:** [MantleDB](https://mantledb.sh/) unclaimed public-write JSON document, configured in `storage.json`. A `PATCH` updates a single banner's fields atomically, without overwriting the entire collection.
- **Realtime update signals:** [ntfy](https://ntfy.sh/) Server-Sent Events tell other open browsers to refresh after a successful save; the notification contains no banner details.
- **Resilience:** Pending edits remain in each browser's local storage until acknowledged by the database, with retries, a clickable connection indicator, and a polling fallback if the push stream disconnects.
- **GitHub backup:** GitHub Actions copies the public store to `banners.json` twice an hour and writes an automated daily heartbeat to prevent free-tier inactivity expiry.
- **Previous browser data:** Existing locally saved entries and unsent changes from the old API are merged into the new collection on the first successful connection.

**Tested:** The `Browser sync smoke test` workflow runs two independent Chromium browser contexts and confirms that adding, renaming, marking Made, and deleting updates both devices, without reloading. It also checks the persisted database. Tests use an isolated namespace to avoid changing your personal banners.

**Security note:** There is intentionally no login. Anyone who discovers the database address can modify entries. Don't store sensitive information. MantleDB and ntfy are separate free third-party services, and their uptime and long-term retention cannot be guaranteed.

## GitHub Pages

Deploy `main` from the repository root in **Settings → Pages**.

## Notes

Minecraft Tools crafting URLs encode dye colors and patterns but not necessarily gallery titles. Dragged gallery HTML may include the title; otherwise rename it manually.

Minecraft textures are Mojang game assets obtained via [MC Assets](https://mcasset.cloud/1.21.9/assets/minecraft/textures/entity/banner). Unofficial fan project.
