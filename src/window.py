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

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", self._on_pointer_enter)
        motion.connect("leave", self._on_pointer_leave)
        overlay.add_controller(motion)

        self.set_content(overlay)
        self.set_default_size(463, 463)
        self.set_resizable(False)

        self.pictureIndex = 0

        self.carousel.connect("page-changed", self.pictureChanged)

        picturesFolder = self.settings.get_string("picture-folder")
        if picturesFolder:
            self.loadPictures(picturesFolder)

        self.settings.connect("changed::picture-folder", self.onFolderSelect)
        self.settings.connect("changed::delay", lambda *args: self.toggleTimer())

        self.toggleTimer()

    def _on_pointer_enter(self, controller, x, y):
        self.close_btn.set_visible(True)

    def _on_pointer_leave(self, controller):
        self.close_btn.set_visible(False)

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
        num = self.carousel.get_n_pages()
        for index in reversed(range(num)):
            print(index)
            print("n: "+str(self.carousel.get_n_pages()))
            self.carousel.remove(self.carousel.get_nth_page(index))

    def onFolderSelect(self, settings, key):
        self.clearCarousel()
        self.loadPictures(settings.get_string(key))


    def loadPictures(self, folder):
        files = list(self.findPictures(Gio.File.new_for_path(folder)))
        random.shuffle(files)
        self.pictureIter = iter(files)
        GLib.idle_add(self.loadNextPicture)

    def loadNextPicture(self):
        try:
            pic = next(self.pictureIter)
        except StopIteration:
            return False  # stop calling

        picture = Gtk.Picture.new_for_file(pic)
        picture.set_content_fit(Gtk.ContentFit.COVER)
        self.carousel.append(picture)


        return True


    def toggleTimer(self):
        try:
            GLib.source_remove(self.timer)
        except Exception:
            pass

        delay = self.settings.get_int("delay")
        self.timer = GLib.timeout_add_seconds(delay, self.changePicture)

    def pictureChanged(self, carousel, index):
        self.pictureIndex = index
        self.toggleTimer()

    def changePicture(self):

        self.pictureIndex = self.pictureIndex + 1

        if (self.pictureIndex == (self.carousel.get_n_pages())):
            self.pictureIndex = 0

        picture = self.carousel.get_nth_page(self.pictureIndex)
        self.carousel.scroll_to(picture, True)
        return True

