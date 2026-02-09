# memories

A picture carousel app for GNOME. Displays images from a folder in random order and advances automatically.

## Building and installing

```bash
meson setup build --prefix=/usr/local   # or --prefix=$HOME/.local for user install
meson compile -C build
meson install -C build                  # use sudo if installing to /usr or /usr/local
```

## Usage

- **Preferences (Ctrl+,):** Choose the picture folder and set the carousel delay (seconds between images).
- **Quit:** Ctrl+Q, Escape, or the close button (top-right, shown when the pointer is over the window).
- **Change picture:** Touchpad swipe gestures, or wait for the timer to advance.
- **Pause:** The carousel pauses while the pointer is inside the window and resumes when it leaves.
- **Display:** Images are scaled to fit the window (aspect ratio preserved).

Images from the selected folder are shown in random order each time the folder is loaded.
