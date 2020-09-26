#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk



class GalleryWidget(Gtk.FlowBox):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
		self.init_ui()

	def init_ui(self):
		...