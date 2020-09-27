#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk	# type: ignore

from widgets.gallery_card import ImageCardWidget
from providers.bing import BingProvider, BingImage



class GalleryWidget(Gtk.FlowBox):

	def __init__(self):
		super().__init__()

		self.prov = BingProvider()
		self.prov.load()
	
		self.init_ui()

	def init_ui(self):
		for entry in self.prov:
			card = ImageCardWidget(entry.date, entry.file)
			self.add(card)