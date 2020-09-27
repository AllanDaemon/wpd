#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk	# type: ignore

from widgets.main_win import MainWindow


# default font-size: 10pt;
app_css = b'* {font-size: 12pt;}'

def main(threaded=True):
	main_win = MainWindow()
	main_win.show_all()

	style_prov = Gtk.CssProvider()
	assert style_prov.load_from_data(app_css)
	Gtk.StyleContext.add_provider_for_screen(
		Gdk.Screen.get_default(),
		style_prov,
		Gtk.STYLE_PROVIDER_PRIORITY_USER
	)

	
	if not threaded:
		Gtk.main()
	else:
		from threading import Thread
		t = Thread(name='GTK Thread', target=Gtk.main)
		t.start()


if __name__ == "__main__":
	main()
