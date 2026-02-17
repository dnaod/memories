# memories

A picture slideshow app for GNOME. Displays images from a folder in random order and advances automatically. Shows one image at a time and keeps memory use low, so it works well with large folders.

## Building and installing

```bash
meson setup build --prefix=/usr/local   # or --prefix=$HOME/.local for user install
meson compile -C build
meson install -C build                  # use sudo if installing to /usr or /usr/local
```

## Usage

- **Settings:** Ctrl+, or the menu button (top-left when the pointer is over the window). Choose the picture folder and set the delay between images. You can include subfolders (depth 1–5).
- **Navigate:** **j** (next) and **k** (previous); or click the left/right third of the window; or swipe left/right on the touchpad; or wait for the timer.
- **Pause:** The slideshow pauses while the pointer is over the window. Use the pause button (bottom-right) to pause or resume manually.
- **Quit:** Ctrl+Q, Escape, or the close button (top-right).
- **GIFs:** Animated GIFs play once then advance; they loop while the pointer is over the window or when paused.

Hovering over the window shows the current image’s filename at the bottom. Images are scaled to fit; the window is resizable.

## Credits

This app is based on [memories](https://github.com/coldsprinkles/memories) by [coldsprinkles](https://github.com/coldsprinkles). This fork is maintained by [dnaod](https://github.com/dnaod/memories). Both are licensed under GPL-3.0-or-later.
