# Banner Tracker

A minimal, client-side Minecraft banner collection for GitHub Pages.

- Paste or drag individual banner crafting links from [Minecraft Tools](https://minecraft.tools/en/banner-galery).
- Designs are added immediately, without pressing Enter.
- Preview banners using local Minecraft pattern textures.
- Rename, open, and remove saved banners.
- Saved banners persist in your browser with localStorage.

## GitHub Pages

Deploy `main` from the repository root in **Settings → Pages**, using **Deploy from a branch**. Then visit `https://ryanehinkle.github.io/mc-banner-tracker/`.

## Notes

Individual `banner.php` URLs encode the patterns and colors, but generally do **not** encode the gallery entry's title. Where a dropped link includes its original HTML link text, the site uses that name; otherwise it assigns a name you can edit. Data stays in your current browser (no account sync).

Banner texture assets are sourced from Mojang's game resources (via [MC Assets](https://mcasset.cloud/1.21.9/assets/minecraft/textures/entity/banner)); Minecraft is a trademark of Mojang/Microsoft, and this fan project is not affiliated with them.
