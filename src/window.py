# window.py
#
# Copyright 2026 riyani
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

import random

from gi.repository import Adw
from gi.repository import Gtk, Gio, GLib

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

        self.carousel.connect("page-changed", self.pictureChanged)

        picturesFolder = self.settings.get_string("picture-folder")
        if picturesFolder:
            self.loadPictures(picturesFolder)

        self.settings.connect("changed::picture-folder", self.onFolderSelect)
        self.settings.connect("changed::delay", lambda *args: self.toggleTimer())

        self.toggleTimer()

    def _on_pointer_enter(self, controller, x, y):
        self.close_btn.set_visible(True)
        self.menu_btn.set_visible(True)
        self.pause_btn.set_visible(True)
        self._pause_carousel_timer()

    def _on_pointer_leave(self, controller):
        self.close_btn.set_visible(False)
        self.menu_btn.set_visible(False)
        if not self._user_paused:
            self.pause_btn.set_visible(False)
            self._resume_carousel_timer()

    def _on_pause_clicked(self, btn):
        self._user_paused = not self._user_paused
        if self._user_paused:
            self._pause_carousel_timer()
        else:
            self.toggleTimer()

    def findPictures(self, gio_file):
        for info in gio_file.enumerate_children(
            'standard::name,standard::type,standard::content-type',
            Gio.FileQueryInfoFlags.NONE,
            None
        ):
            child = gio_file.get_child(info.get_name())

            if info.get_file_type() == Gio.FileType.DIRECTORY:
                yield from self.findPictures(child)
            else:
                ct = info.get_content_type()
                if ct and ct.startswith("image"):
                    yield child

    def clearCarousel(self):
        for index in reversed(range(self.carousel.get_n_pages())):
            self.carousel.remove(self.carousel.get_nth_page(index))
        self._picture = None

    def onFolderSelect(self, settings, key):
        self.clearCarousel()
        self.loadPictures(settings.get_string(key))

    def _file_at(self, index):
        n = len(self._file_list)
        if n == 0:
            return None
        return self._file_list[index % n]

    def _update_picture(self):
        if len(self._file_list) == 0 or self._picture is None:
            return
        self._picture.set_file(self._file_at(self._current_index))

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
        return False

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
        self._file_list = list(self.findPictures(Gio.File.new_for_path(folder)))
        if not self._file_list:
            return
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

