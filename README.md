# memories

A picture slideshow app for GNOME. Displays images from a folder in random order and advances automatically. Shows one image at a time and keeps memory use low, so it works well with large folders (e.g. 2000+ images).

## Building and installing

```bash
meson setup build --prefix=/usr/local   # or --prefix=$HOME/.local for user install
meson compile -C build
meson install -C build                  # use sudo if installing to /usr or /usr/local
```

## Usage

- **Settings:** Ctrl+, or the menu button (top-left, shown when the pointer is over the window). Choose the picture folder and set the delay (seconds between images).
- **Quit:** Ctrl+Q, Escape, or the close button (top-right, shown when the pointer is over the window).
- **Change picture:** Click the left third of the window for previous, the right third for next; or use touchpad swipe (left/right); or wait for the timer to advance.
- **Pause:** The slideshow pauses while the pointer is inside the window and resumes when it leaves. The pause button (bottom-right, shown with the other controls) toggles a manual pause: when paused, the timer stops and the button stays visible even after the pointer leaves; click again to unpause.
- **Display:** Images are scaled to fit the window (aspect ratio preserved). The window is resizable.

Images from the selected folder are shown in random order each time the folder is loaded.
