# Minecraft Banner Tracker

A minimal, mobile-friendly Minecraft banner collection built for GitHub Pages.

## Features

- Paste or drag a banner link from [Minecraft Tools](https://minecraft.tools/en/banner-galery). It imports automatically, with no Enter key needed.
- Banner thumbnails are drawn locally with vanilla Minecraft banner textures.
- Rename banners, open their original designs, mark them as made, and filter the visible collection.
- The **My banners** count follows the current filter.
- A shared `banners.json` in this repository is the source of truth, so saved changes are visible on every device.

## Cross-device GitHub sync

**Viewing:** Anyone can view the shared collection without signing in. The site fetches `banners.json` from GitHub on load and periodically when open.

**Editing:** GitHub Pages is a static website and cannot securely update repository files anonymously. To save changes permanently:

1. In GitHub, [create a fine-grained personal access token](https://github.com/settings/personal-access-tokens/new).
2. Limit **Repository access** to **Only select repositories → ryanehinkle/mc-banner-tracker**.
3. Give **Repository permissions → Contents → Read and write**. Leave other permissions at their defaults.
4. On the tracker, click the cloud icon in the header, paste the token, and choose **Connect & sync**.

The token is kept only in that browser's local storage, **never committed or uploaded into the site's files**. Other devices can view changes immediately; to **edit** on another device, connect a token there too.

The tracker automatically imports existing banner entries from the previous local-only version the first time it loads the new version. Any edits made while disconnected are retained locally and uploaded when connected.

**Security:** Treat your token as a password. Don't share it or commit it to source control. If a device is shared, click **Disconnect this device** and clear its stored website data when you're done. You can revoke the token in GitHub settings.

## Deployment

Enable **Settings → Pages → Deploy from a branch → main → / (root)**. Open:

https://ryanehinkle.github.io/mc-banner-tracker/

## Notes

Minecraft Tools banner URLs encode the pattern and dye colors but do not encode the public gallery title. Dragged HTML links may include their gallery title. Otherwise you can edit the initial name yourself.

Textures are from Mojang's game assets, via [MC Assets](https://mcasset.cloud/1.21.9/assets/minecraft/textures/entity/banner). Minecraft is a trademark of Mojang/Microsoft; this fan project is unofficial.
