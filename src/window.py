# window.py – main window and slideshow logic
#
# Copyright (C) coldsprinkles (https://github.com/coldsprinkles/memories)
# Copyright (C) 2026 dnaod (https://github.com/dnaod/memories)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import random

from gi.repository import Adw
from gi.repository import Gdk, Gtk, Gio, GLib

class MemoriesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MemoriesWindow'


    """def selectFolder(self):
            file_dialog = Gtk.FileDialog()
            file_dialog.select_folder(self, None, self.onSingleSelected)

    def onSingleSelected(self, file_dialog, result):
        folder = file_dialog.select_folder_finish(result)
        selectedFolder = self.getFolder(folder)
        self.loadPictures(selectedFolder)
        print(f"Selected Folder: {selectedFolder}")

    def getFolder(self, folder):
        return folder.get_path()
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.get_application().settings


        #self.selectFolder()


        self.carousel = Adw.Carousel()
        self.carousel.set_allow_mouse_drag(False)
        self.carousel.set_hexpand(True)
        self.carousel.set_vexpand(True)


        windowHandle = Gtk.WindowHandle()
        windowHandle.set_child(self.carousel)

        overlay = Gtk.Overlay()
        overlay.set_child(windowHandle)

        self.close_btn = Gtk.Button()
        self.close_btn.set_icon_name("window-close-symbolic")
        self.close_btn.add_css_class("circular")
        self.close_btn.set_halign(Gtk.Align.END)
        self.close_btn.set_valign(Gtk.Align.START)
        self.close_btn.set_margin_top(12)
        self.close_btn.set_margin_end(12)
        self.close_btn.set_visible(False)
        self.close_btn.connect("clicked", lambda *_: self.close())
        overlay.add_overlay(self.close_btn)

        self.menu_btn = Gtk.Button()
        self.menu_btn.set_icon_name("open-menu-symbolic")
        self.menu_btn.add_css_class("circular")
        self.menu_btn.set_halign(Gtk.Align.START)
        self.menu_btn.set_valign(Gtk.Align.START)
        self.menu_btn.set_margin_top(12)
        self.menu_btn.set_margin_start(12)
        self.menu_btn.set_visible(False)
        self.menu_btn.connect(
            "clicked",
            lambda *_: self.get_application().activate_action("preferences", None),
        )
        overlay.add_overlay(self.menu_btn)

        self.pause_btn = Gtk.Button()
        self.pause_btn.set_icon_name("media-playback-pause-symbolic")
        self.pause_btn.add_css_class("circular")
        self.pause_btn.set_halign(Gtk.Align.END)
        self.pause_btn.set_valign(Gtk.Align.END)
        self.pause_btn.set_margin_end(12)
        self.pause_btn.set_margin_bottom(12)
        self.pause_btn.set_visible(False)
        self.pause_btn.connect("clicked", self._on_pause_clicked)
        overlay.add_overlay(self.pause_btn)

        self.filename_label = Gtk.Label()
        self.filename_label.add_css_class("filename-overlay")
        self.filename_label.set_halign(Gtk.Align.CENTER)
        self.filename_label.set_valign(Gtk.Align.END)
        self.filename_label.set_margin_bottom(12)
        self.filename_label.set_visible(False)
        self.filename_label.set_selectable(True)
        overlay.add_overlay(self.filename_label)

        self._empty_message_label = Gtk.Label(label="Please choose a Picture Folder")
        self._empty_message_label.set_halign(Gtk.Align.CENTER)
        self._empty_message_label.set_valign(Gtk.Align.CENTER)
        self._empty_message_label.set_visible(False)
        overlay.add_overlay(self._empty_message_label)

        filename_css = Gtk.CssProvider()
        filename_css.load_from_data(b".filename-overlay { font-size: 11px; }")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            filename_css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", self._on_pointer_enter)
        motion.connect("leave", self._on_pointer_leave)
        overlay.add_controller(motion)

        self._swipe = Gtk.GestureSwipe()
        self._swipe.connect("end", self._on_swipe_end)
        overlay.add_controller(self._swipe)

        click = Gtk.GestureClick()
        click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        click.connect("pressed", self._on_click_pressed)
        overlay.add_controller(click)

        self.set_content(overlay)

        key = Gtk.EventControllerKey()
        key.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key)
        self.set_default_size(463, 463)
        self.set_resizable(True)

        self.pictureIndex = 0
        self.timer = None
        self._user_paused = False
        self._file_list = []
        self._current_index = 0
        self._picture = None  # single Gtk.Picture widget
        self._gif_media = None  # Gtk.MediaFile when showing a GIF
        self._gif_ended_id = None  # handler id for notify::ended
        self._pointer_over = False  # pointer within window bounds
        self._root_folder = None  # picture-folder path, for relative filename display
        self._delete_pending = False  # True while delete confirmation dialog is open

        self.carousel.connect("page-changed", self.pictureChanged)

        picturesFolder = self.settings.get_string("picture-folder")
        if picturesFolder:
            self.loadPictures(picturesFolder)
        if not self._file_list:
            self._empty_message_label.set_visible(True)

        self.settings.connect("changed::picture-folder", self.onFolderSelect)
        self.settings.connect(
            "changed::include-subfolders", self._on_include_subfolders_changed
        )
        self.settings.connect(
            "changed::subfolder-depth", self._on_subfolder_depth_changed
        )
        self.settings.connect("changed::delay", lambda *args: self.toggleTimer())

        self.toggleTimer()

    def _on_pointer_enter(self, controller, x, y):
        self._pointer_over = True
        self.close_btn.set_visible(True)
        self.menu_btn.set_visible(True)
        self.pause_btn.set_visible(True)
        self._update_filename_label()
        self.filename_label.set_visible(True)
        self._pause_carousel_timer()
        self._apply_gif_loop_state()

    def _on_pointer_leave(self, controller):
        self._pointer_over = False
        self.close_btn.set_visible(False)
        self.menu_btn.set_visible(False)
        self.filename_label.set_visible(False)
        if not self._user_paused:
            self.pause_btn.set_visible(False)
            self._resume_carousel_timer()
        self._apply_gif_loop_state()

    def _update_filename_label(self):
        current = self._file_at(self._current_index)
        if current is not None:
            path = current.get_path()
            if path and self._root_folder:
                root = self._root_folder.rstrip(os.sep) or self._root_folder
                if path.startswith(root) and (
                    len(path) == len(root) or path[len(root)] == "/"
                ):
                    rel = path[len(root):].lstrip(os.sep)
                    if rel:
                        name = rel
                    else:
                        name = current.get_basename() or ""
                else:
                    name = current.get_basename() or ""
            else:
                name = current.get_basename() or ""
            self.filename_label.set_label(name)
        else:
            self.filename_label.set_label("")

    def _gif_should_loop(self):
        return self._user_paused or self._pointer_over

    def _apply_gif_loop_state(self):
        if self._gif_media is None:
            return
        should_loop = self._gif_should_loop()
        self._gif_media.set_loop(should_loop)
        if self._gif_ended_id is not None:
            self._gif_media.disconnect(self._gif_ended_id)
            self._gif_ended_id = None
        if not should_loop:
            self._gif_ended_id = self._gif_media.connect(
                "notify::ended", self._on_gif_ended
            )

    def _on_pause_clicked(self, btn):
        self._user_paused = not self._user_paused
        self._apply_gif_loop_state()
        if self._user_paused:
            self._pause_carousel_timer()
        else:
            self.toggleTimer()

    def findPictures(self, gio_file, depth=0, max_depth=2):
        for info in gio_file.enumerate_children(
            'standard::name,standard::type,standard::content-type',
            Gio.FileQueryInfoFlags.NONE,
            None
        ):
            name = info.get_name()
            child = gio_file.get_child(name)

            if info.get_file_type() == Gio.FileType.DIRECTORY:
                if name.startswith("."):
                    continue
                if depth < max_depth:
                    yield from self.findPictures(child, depth + 1, max_depth)
            else:
                ct = info.get_content_type()
                if ct and ct.startswith("image"):
                    yield child

    def clearCarousel(self):
        self._clear_current_gif()
        for index in reversed(range(self.carousel.get_n_pages())):
            self.carousel.remove(self.carousel.get_nth_page(index))
        self._picture = None

    def onFolderSelect(self, settings, key):
        self.clearCarousel()
        self.loadPictures(settings.get_string(key))

    def _on_include_subfolders_changed(self, settings, key):
        folder = settings.get_string("picture-folder")
        if folder:
            self.clearCarousel()
            self.loadPictures(folder)

    def _on_subfolder_depth_changed(self, settings, key):
        if not settings.get_boolean("include-subfolders"):
            return
        folder = settings.get_string("picture-folder")
        if folder:
            self.clearCarousel()
            self.loadPictures(folder)

    def _file_at(self, index):
        n = len(self._file_list)
        if n == 0:
            return None
        return self._file_list[index % n]

    def _is_gif(self, gio_file):
        path = gio_file.get_path()
        return path is not None and path.lower().endswith(".gif")

    def _clear_current_gif(self):
        if self._gif_ended_id is not None and self._gif_media is not None:
            self._gif_media.disconnect(self._gif_ended_id)
        self._gif_ended_id = None
        self._gif_media = None
        if self._picture is not None:
            self._picture.set_paintable(None)

    def _on_gif_ended(self, media, param_spec):
        if not self._gif_should_loop():
            self._go_next()

    def _update_picture(self):
        if len(self._file_list) == 0 or self._picture is None:
            return

        self._clear_current_gif()
        current = self._file_at(self._current_index)
        if current is None:
            return

        self._update_filename_label()
        if self._is_gif(current):
            self._gif_media = Gtk.MediaFile.new_for_file(current)
            self._picture.set_file(None)
            self._picture.set_paintable(self._gif_media)
            self._apply_gif_loop_state()
            self._gif_media.set_playing(True)
            self._pause_carousel_timer()
        else:
            self._picture.set_file(current)
            self.toggleTimer()

    def _go_next(self):
        if len(self._file_list) == 0:
            return
        self._current_index = (self._current_index + 1) % len(self._file_list)
        self._update_picture()
        self.toggleTimer()

    def _go_previous(self):
        if len(self._file_list) == 0:
            return
        self._current_index = (self._current_index - 1) % len(self._file_list)
        self._update_picture()
        self.toggleTimer()

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == ord("j"):
            self._go_next()
            return True
        if keyval == ord("k"):
            self._go_previous()
            return True
        if keyval == ord("d"):
            self._confirm_delete_image()
            return True
        return False

    def _confirm_delete_image(self):
        if not self._file_list:
            return
        current = self._file_at(self._current_index)
        if current is None:
            return

        self._delete_pending = True
        self._pause_carousel_timer()

        path = current.get_path() or current.get_basename() or ""
        dialog = Adw.AlertDialog(
            heading="Delete Image?",
            body=path,
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance(
            "delete", Adw.ResponseAppearance.DESTRUCTIVE
        )
        dialog.set_default_response("delete")
        dialog.set_close_response("cancel")
        dialog.connect("response", self._on_delete_response, current)
        dialog.present(self)

    def _on_delete_response(self, dialog, response, gio_file):
        self._delete_pending = False
        if response == "delete":
            try:
                gio_file.delete(None)
            except Exception:
                self._resume_carousel_timer()
                return
            try:
                self._file_list.remove(gio_file)
            except ValueError:
                pass
            if not self._file_list:
                self.clearCarousel()
                self._empty_message_label.set_visible(True)
            else:
                if self._current_index >= len(self._file_list):
                    self._current_index = 0
                self._update_picture()
        self._resume_carousel_timer()

    def _on_swipe_end(self, gesture, x, y):
        dx, dy = gesture.get_velocity()
        if dx < -100:
            self._go_next()
        elif dx > 100:
            self._go_previous()

    def _point_in_widget(self, widget, x, y):
        alloc = widget.get_allocation()
        return alloc.x <= x < alloc.x + alloc.width and alloc.y <= y < alloc.y + alloc.height

    def _on_click_pressed(self, gesture, n_press, x, y):
        overlay = gesture.get_widget()
        if (
            self._point_in_widget(self.close_btn, x, y)
            or self._point_in_widget(self.menu_btn, x, y)
            or self._point_in_widget(self.pause_btn, x, y)
        ):
            return
        w = overlay.get_allocated_width()
        if x < w / 3:
            self._go_previous()
        elif x >= 2 * w / 3:
            self._go_next()

    def loadPictures(self, folder):
        self._root_folder = os.path.abspath(folder)
        if self.settings.get_boolean("include-subfolders"):
            max_depth = max(1, min(5, self.settings.get_int("subfolder-depth")))
        else:
            max_depth = 0
        try:
            self._file_list = list(
                self.findPictures(
                    Gio.File.new_for_path(folder), max_depth=max_depth
                )
            )
        except Exception:
            self._file_list = []
            self.settings.set_string("picture-folder", "")
        if not self._file_list:
            self._empty_message_label.set_visible(True)
            return
        self._empty_message_label.set_visible(False)
        random.shuffle(self._file_list)
        self._current_index = 0

        self._picture = Gtk.Picture()
        self._picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        self.carousel.append(self._picture)
        self._update_picture()


    def _pause_carousel_timer(self):
        if self.timer is not None:
            try:
                GLib.source_remove(self.timer)
            except Exception:
                pass
            self.timer = None

    def _resume_carousel_timer(self):
        if not self._user_paused:
            self.toggleTimer()

    def toggleTimer(self):
        if self.timer is not None:
            try:
                GLib.source_remove(self.timer)
            except Exception:
                pass
            self.timer = None

        if self._delete_pending:
            return

        delay = self.settings.get_int("delay")
        self.timer = GLib.timeout_add_seconds(delay, self.changePicture)

    def pictureChanged(self, carousel, index):
        self.pictureIndex = index
        self.toggleTimer()

    def changePicture(self):
        if len(self._file_list) == 0:
            return True
        self._current_index = (self._current_index + 1) % len(self._file_list)
        self._update_picture()
        return True

