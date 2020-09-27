#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk	# type: ignore
from gi.repository.GdkPixbuf import Pixbuf, InterpType	# type: ignore



class ImageCardWidget(Gtk.Button):
	CARD_WIDTH = 300

	def __init__(self, date: str, f_path: Path):
		super().__init__()
		self.date = date
		self.f_path = f_path
	
		self.init_ui()

	def init_ui(self):
		self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.add(self.box)

		pb = Pixbuf.new_from_file(str(self.f_path))
		o_w, o_h = pb.get_width(), pb.get_height()
		ratio = self.CARD_WIDTH / o_w
		n_h = o_h * ratio
		spb = pb.scale_simple(self.CARD_WIDTH, n_h, InterpType.BILINEAR)
		im = Gtk.Image.new_from_pixbuf(spb)
		# im = Gtk.Image.new_from_file(str(self.f_path))
		self.box.pack_start(im, False, False, 0)

		label = Gtk.Label.new(f'Date: {self.date}')
		self.box.pack_start(label, False, False, 0)
