#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from widgets.source_chooser import SourceChooserWidget



class MainHeaderBarWidget(Gtk.HeaderBar):

	def __init__(self, *args, **kwargs):
		kwargs['title'] = "WPD"
		kwargs['show_close_button'] = True
		super().__init__(*args, **kwargs)
	
		self.init_ui()

	def init_ui(self):
		self.src_ch = SourceChooserWidget()
		self.pack_start(Gtk.Label.new("Source"))
		self.pack_start(self.src_ch)
