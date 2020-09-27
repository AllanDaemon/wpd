#!/usr/bin/env python3

from __future__ import annotations
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk	# type: ignore
from gi.repository.GdkPixbuf import Pixbuf	# type: ignore



ASSETS_DIR = Path('widgets/assets')

def _icon(f_name:str) -> Pixbuf:
	f_path: Path = ASSETS_DIR / f_name
	return Pixbuf.new_from_file_at_size(str(f_path), 16, 16)

model_data = [
	('apod', _icon("nasa-logo.svg"), "NASA APOD"),
	('bing', _icon("bing-logo.svg"), "BING POTD"),
	('commons', _icon("commons-logo.svg"), "Wiki Commons POTD"),
]

class SourceChooserWidget(Gtk.ComboBox):

	def __init__(self):
		model = self.build_model()
		super().__init__(model=model)	# type: ignore
	
		self.init_ui()

	def build_model(self):
		model = Gtk.ListStore(str, Pixbuf, str)
		for entry in model_data:
			model.append(entry)
		return model

	def init_ui(self):
		renderer_ico = Gtk.CellRendererPixbuf()
		renderer_txt = Gtk.CellRendererText()
		self.pack_start(renderer_ico, False)
		self.pack_start(renderer_txt, True)
		self.add_attribute(renderer_ico, "pixbuf", 1)
		self.add_attribute(renderer_txt, "text", 2)

