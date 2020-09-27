#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from widgets.header_bar import MainHeaderBarWidget
from widgets.gallery import GalleryWidget



class MainWindow(Gtk.Window):

	def __init__(self, *args, **kwargs):
		kwargs['title'] = "WPD"
		kwargs['default_width'] = 900
		kwargs['default_height'] = 500
		super().__init__(*args, **kwargs)
		self.connect("destroy", Gtk.main_quit)
	
		self.init_ui()

	def init_ui(self):
		hb = MainHeaderBarWidget()
		gallery = GalleryWidget()

		self.set_titlebar(hb)
		self.add(gallery)