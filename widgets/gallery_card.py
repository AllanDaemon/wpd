#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk



class ImageCardWidget(Gtk.Box):

	def __init__(self):
		super().__init__()
	
		self.init_ui()

	def init_ui(self):
		...