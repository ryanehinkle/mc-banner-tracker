# Minecraft Banner Tracker

A minimal, mobile-friendly Minecraft banner collection built for GitHub Pages.

[Open Banner Tracker](https://ryanehinkle.github.io/mc-banner-tracker/)

## Features

- Paste or drag a banner link from [Minecraft Tools](https://minecraft.tools/en/banner-galery). Valid links import automatically.
- Preview banner patterns using bundled Minecraft textures.
- Rename banners, open their designs, mark them as made, and filter by status.
- **My banners** shows the number of visible banners under the current filter.
- **Automatic cross-device sync, with no login or token required.** 

## How sharing works

The site's live collection is stored in a shared public REST database record, whose address is in `storage.json`. Every add, rename, checkbox change, or removal updates this document. Any device opening the site reads the same collection. The small dot in the header is green when fully synced and amber if local edits are waiting to sync.

GitHub Actions (see `.github/workflows/sync-banners.yml`) initializes the shared document automatically and copies its contents into the repository's `banners.json` at regular intervals. Existing local browser data is migrated automatically and queued changes are retried whenever the site is visited.

**Important:** This is intentionally a no-login, publicly writable collection, per the project's zero-friction design. Anyone who finds the shared storage URL can edit or delete entries. Do not use it for private or sensitive data. The repository's regularly updated `banners.json` provides a backup, but this free third-party service is intended for prototypes and is not a guaranteed permanent or highly available database.

## Deployment

Settings → Pages → Deploy from a branch → `main` → `/ (root)`.

Provisioning is handled automatically by GitHub Actions, which writes `storage.json`. The workflow backs up the live collection to `banners.json` twice an hour.

## Notes

Minecraft Tools links encode patterns and colors but not necessarily gallery titles. Dragged gallery HTML can include the title; otherwise rename the entry.

Minecraft textures are Mojang assets obtained via [MC Assets](https://mcasset.cloud/1.21.9/assets/minecraft/textures/entity/banner). This is an unofficial fan project.
