# memories

A picture slideshow app for GNOME. Displays images from a folder in random order and advances automatically. You can include images from subfolders (with configurable depth, 1–5 levels). Shows one image at a time and keeps memory use low, so it works well with large folders (e.g. 2000+ images).

## Building and installing

```bash
meson setup build --prefix=/usr/local   # or --prefix=$HOME/.local for user install
meson compile -C build
meson install -C build                  # use sudo if installing to /usr or /usr/local
```

The app icon is installed from `data/icons/` (hicolor scalable and symbolic) and is used by the GNOME shell and desktop entry.

## Usage

- **Settings:** Ctrl+, or the menu button (top-left, shown when the pointer is over the window). Choose the picture folder, set the delay (seconds between images), and optionally enable **Include Subfolders** with a **Depth** (1–5) for how many levels of subfolders to scan. Hidden directories (names starting with `.`) are always skipped.
- **Quit:** Ctrl+Q, Escape, or the close button (top-right, shown when the pointer is over the window).
- **Change picture:** **j** (next) and **k** (previous), vim-style; or click the left third of the window for previous, the right third for next; or use touchpad swipe (left/right); or wait for the timer to advance.
- **Pause:** The slideshow pauses while the pointer is inside the window and resumes when it leaves. The pause button (bottom-right, shown with the other controls) toggles a manual pause: when paused, the timer stops and the button stays visible even after the pointer leaves; click again to unpause.
- **Display:** Images are scaled to fit the window (aspect ratio preserved). The window is resizable.
- **GIFs:** Animated GIFs play once and then the slideshow advances to the next file. While the pointer is over the window or the slideshow is paused, GIFs loop instead of advancing.

Images from the selected folder (and optionally its subfolders, per settings) are shown in random order each time the folder is loaded. When the pointer is over the window, the current image’s filename is shown at the bottom; if the image is in a subfolder, the path relative to the picture folder (e.g. `2024/vacation/beach.jpg`) is displayed. If the saved picture folder is unavailable at startup (e.g. removed or unmounted), the app still opens, shows “Please choose a Picture Folder” in the centre, and clears the setting; the folder chooser opens to the current picture folder when that folder is available.

## Credits

This app is based on [memories](https://github.com/coldsprinkles/memories) by [coldsprinkles](https://github.com/coldsprinkles). This fork is maintained by [dnaod](https://github.com/dnaod/memories). Both are licensed under GPL-3.0-or-later.
